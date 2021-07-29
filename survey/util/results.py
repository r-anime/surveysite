from dataclasses import dataclass
from django.core.cache import caches
from django.db.models import Avg
from enum import Enum
from json import JSONEncoder
from survey.models import Anime, AnimeResponse, Response, Survey, SurveyAdditionRemoval
from survey.util.anime import get_image_url_list, get_name_list
from survey.util.survey import get_survey_anime, get_survey_cache_timeout


class ResultsType(Enum):
    """Enum representing all types of result values."""
    POPULARITY                  = "Popularity"
    POPULARITY_MALE             = "Popularity (Male)"
    POPULARITY_FEMALE           = "Popularity (Female)"
    GENDER_POPULARITY_RATIO     = "Gender Ratio (♂:♀)"
    GENDER_POPULARITY_RATIO_INV = "Gender Ratio (♀:♂)"
    UNDERWATCHED                = "Underwatched"
    SCORE                       = "Score"
    SCORE_MALE                  = "Score (Male)"
    SCORE_FEMALE                = "Score (Female)"
    GENDER_SCORE_DIFFERENCE     = "Gender Score Difference (♂-♀)"
    GENDER_SCORE_DIFFERENCE_INV = "Gender Score Difference (♀-♂)"
    SURPRISE                    = "Surprise"
    DISAPPOINTMENT              = "Disappointment"
    AGE                         = "Average Viewer Age"
    NAME                        = "Anime" # Only used to be able to sort by this column

AnimeResultsDataType = dict[ResultsType, float]
ResultsDataType = dict[Anime, AnimeResultsDataType]

class ResultsGenerator:
    """Class for generating survey results."""

    def __init__(self, survey: Survey):
        """Creates a survey results generator.

        Parameters
        ----------
        survey : Survey
            The survey for which results have to be generated.
        """
        self.survey = survey

    def get_anime_results_data_json(self):
        anime_series_data, special_anime_data = self.get_anime_results_data()
        encoder = JSONEncoder()

        anime_info_json = encoder.encode({
            anime.id: {
                'official_name_list': get_name_list(anime),
                'type': anime.anime_type,
                'image_list': [image_data.to_dict() for image_data in get_image_url_list(anime)],
            } for anime in list(anime_series_data.keys()) + list(special_anime_data.keys())
        })

        def convert_data(anime_data):
            return encoder.encode({
                anime.id: {
                    results_type.name.lower(): value for results_type, value in results.items()
                } for anime, results in anime_data.items()
            })

        return anime_info_json, convert_data(anime_series_data), convert_data(special_anime_data)

    def get_anime_results_data(self) -> tuple[ResultsDataType, ResultsDataType]:
        """Obtains the results for the survey provided when initializing, either from the cache or generated from database data.

        Returns
        -------
        ({Anime: {ResultsType: any}}, {Anime: {ResultsType: any}})
            A dict for anime series and one for special anime, where each anime has an associated dict of result values.
        """
        if self.survey.state != Survey.State.FINISHED:
            return self.__get_anime_results_data_internal()
        else:
            cache_timeout = get_survey_cache_timeout(self.survey)
            return caches['long'].get_or_set('survey_results_%i' % self.survey.id, self.__get_anime_results_data_internal, version=3, timeout=cache_timeout)

    def __get_anime_results_data_internal(self) -> tuple[ResultsDataType, ResultsDataType]:
        survey = self.survey

        _, anime_series_list, special_anime_list = get_survey_anime(survey)
        animeresponse_queryset = AnimeResponse.objects.filter(response__survey=survey)
        surveyadditionsremovals_queryset = SurveyAdditionRemoval.objects.filter(survey=survey)

        total_response_count = Response.objects.filter(survey=survey).count()
        total_male_response_count = Response.objects.filter(survey=survey, gender=Response.Gender.MALE).count()
        total_female_response_count = Response.objects.filter(survey=survey, gender=Response.Gender.FEMALE).count()

        # Get a dict of data values for each anime (i.e. a dict with for each anime a dict with data values, dict[anime][data])
        anime_series_data = {
            anime: self.__get_data_for_anime(anime, animeresponse_queryset, surveyadditionsremovals_queryset, total_response_count, total_male_response_count, total_female_response_count) for anime in anime_series_list
        }
        special_anime_data = {
            anime: self.__get_data_for_anime(anime, animeresponse_queryset, surveyadditionsremovals_queryset, total_response_count, total_male_response_count, total_female_response_count) for anime in special_anime_list
        }
        return anime_series_data, special_anime_data

    # Returns a dict of data values for an anime
    def __get_data_for_anime(self, anime, animeresponse_queryset, surveyadditionsremovals_queryset, total_response_count, total_male_response_count, total_female_response_count) -> AnimeResultsDataType:
        survey = self.survey

        anime_animeresponse_qs = animeresponse_queryset.filter(anime=anime)
        watchers_animeresponse_qs = anime_animeresponse_qs.filter(watching=True)

        # Adjust response count for this anime taking into account the times the anime was added/removed to the survey
        addition_removal_list = list(surveyadditionsremovals_queryset.filter(anime=anime))
        scaled_total_response_count = self.__get_adjusted_response_count(addition_removal_list, total_response_count)

        # Amount of people watching
        watcher_response_count = watchers_animeresponse_qs.count()
        male_watcher_response_count = watchers_animeresponse_qs.filter(response__gender=Response.Gender.MALE).count()
        female_watcher_response_count = watchers_animeresponse_qs.filter(response__gender=Response.Gender.FEMALE).count()

        male_popularity = div0(male_watcher_response_count, total_male_response_count)
        female_popularity = div0(female_watcher_response_count, total_female_response_count)
        gender_popularity_ratio = div0(male_popularity, female_popularity)
        gender_popularity_ratio_inv = div0(female_popularity, male_popularity)

        score_animeresponse_qs = anime_animeresponse_qs.filter(score__isnull=False) if survey.is_preseason else watchers_animeresponse_qs.filter(score__isnull=False)
        # The aggregate becomes None when there are no scores which causes errors, hence "or NaN" being necessary
        average_score = score_animeresponse_qs.aggregate(Avg('score'))['score__avg'] or float('NaN')
        male_average_score = score_animeresponse_qs.filter(response__gender=Response.Gender.MALE).aggregate(Avg('score'))['score__avg'] or float('NaN')
        female_average_score = score_animeresponse_qs.filter(response__gender=Response.Gender.FEMALE).aggregate(Avg('score'))['score__avg'] or float('NaN')

        return {
            ResultsType.POPULARITY:                  div0(       watcher_response_count, scaled_total_response_count) * 100.0,
            ResultsType.POPULARITY_MALE:             div0(  male_watcher_response_count,   total_male_response_count) * 100.0,
            ResultsType.POPULARITY_FEMALE:           div0(female_watcher_response_count, total_female_response_count) * 100.0,
            ResultsType.GENDER_POPULARITY_RATIO:     gender_popularity_ratio,
            ResultsType.GENDER_POPULARITY_RATIO_INV: gender_popularity_ratio_inv,
            ResultsType.UNDERWATCHED:                div0(watchers_animeresponse_qs.filter(underwatched=True).count(), watcher_response_count) * 100.0,
            ResultsType.SCORE:                              average_score,
            ResultsType.SCORE_MALE:                    male_average_score,
            ResultsType.SCORE_FEMALE:                female_average_score,
            ResultsType.GENDER_SCORE_DIFFERENCE:     male_average_score - female_average_score if min(male_average_score, female_average_score) > 0 else float('NaN'),
            ResultsType.GENDER_SCORE_DIFFERENCE_INV: female_average_score - male_average_score if min(male_average_score, female_average_score) > 0 else float('NaN'),
            ResultsType.SURPRISE:                    div0(watchers_animeresponse_qs.filter(expectations=AnimeResponse.Expectations.SURPRISE      ).count(), watcher_response_count) * 100.0,
            ResultsType.DISAPPOINTMENT:              div0(watchers_animeresponse_qs.filter(expectations=AnimeResponse.Expectations.DISAPPOINTMENT).count(), watcher_response_count) * 100.0,
            ResultsType.AGE:                         watchers_animeresponse_qs.aggregate(avg_age=Avg('response__age'))['avg_age'] or float('NaN'),
        }

    def __get_adjusted_response_count(self, addition_removal_list: list[SurveyAdditionRemoval], response_count: int) -> int:
        i = 0
        last_count = 0
        adjusted_response_count = response_count

        while i < len(addition_removal_list):
            # If addition, addition's count - last count, and move index one up
            if addition_removal_list[i].is_addition:
                addition_count = addition_removal_list[i].response_count
                removal_count = last_count

                adjusted_response_count -= addition_count - removal_count
                last_count = addition_count
                i += 1
            
            # If removal, next addition's count - this removal's count, move index to after addition
            else:
                removal_count = addition_removal_list[i].response_count
                addition_count = response_count
                i += 1
                
                # Try to find index of next addition
                while i < len(addition_removal_list) and not addition_removal_list[i].is_addition:
                    i += 1
                addition_count = addition_removal_list[i].response_count if i < len(addition_removal_list) else response_count

                adjusted_response_count -= addition_count - removal_count
                last_count = addition_count
                i += 1

        return adjusted_response_count


def div0(a: float, b: float) -> float:
    return a / b if b > 0 else float('NaN')
