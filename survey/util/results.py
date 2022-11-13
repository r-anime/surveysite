from typing import Any, Union
from django.core.cache import caches
from django.db.models import Avg
from django.db.models.manager import BaseManager
import math
from survey.models import Anime, AnimeResponse, Response, Survey, SurveyAdditionRemoval
from survey.util.data import ResultType
from survey.util.survey import get_survey_anime, get_survey_cache_timeout


class ResultsGenerator:
    """Class for generating survey results."""
    survey: Survey

    def __init__(self, survey: Survey):
        """Creates a survey results generator.

        Parameters
        ----------
        survey : Survey
            The survey for which results have to be generated.
        """
        self.survey = survey

    def get_anime_results_data(self) -> dict[int, dict[ResultType, float]]:
        """Obtains the results for the survey provided when initializing, either from the cache or generated from database data.

        Returns
        -------
        {anime_id: {ResultType: float}}
            A dict where each anime has an associated dict of result values.
        """
        if self.survey.state != Survey.State.FINISHED:
            return self.__get_anime_results_data_internal()
        else:
            cache_timeout = get_survey_cache_timeout(self.survey)
            return caches['long'].get_or_set('survey_results_%i' % self.survey.id, self.__get_anime_results_data_internal, version=8, timeout=cache_timeout)

    def __get_anime_results_data_internal(self) -> dict[int, dict[ResultType, float]]:
        survey = self.survey

        anime_list, _, _ = get_survey_anime(survey)
        animeresponse_queryset = AnimeResponse.objects.filter(response__survey=survey)
        surveyadditionsremovals_queryset = SurveyAdditionRemoval.objects.filter(survey=survey)

        total_response_count = Response.objects.filter(survey=survey).count()
        total_male_response_count = Response.objects.filter(survey=survey, gender=Response.Gender.MALE).count()
        total_female_response_count = Response.objects.filter(survey=survey, gender=Response.Gender.FEMALE).count()

        # Get a dict of data values for each anime (i.e. a dict with for each anime a dict with data values, dict[anime][data])
        return {
            anime.id: self.__get_data_for_anime(anime, animeresponse_queryset, surveyadditionsremovals_queryset, total_response_count, total_male_response_count, total_female_response_count) for anime in anime_list
        }

    # Returns a dict of data values for an anime
    def __get_data_for_anime(self, anime: Anime, animeresponse_queryset: BaseManager[AnimeResponse], surveyadditionsremovals_queryset: BaseManager[SurveyAdditionRemoval], total_response_count: int, total_male_response_count: int, total_female_response_count: int) -> dict[ResultType, float]:
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

        score_animeresponse_qs = anime_animeresponse_qs.filter(score__isnull=False) if survey.is_preseason else watchers_animeresponse_qs.filter(score__isnull=False)
        # The aggregate becomes None when there are no scores which causes errors, hence "or NaN" being necessary
        average_score = score_animeresponse_qs.aggregate(Avg('score'))['score__avg'] or float('NaN')
        male_average_score = score_animeresponse_qs.filter(response__gender=Response.Gender.MALE).aggregate(Avg('score'))['score__avg'] or float('NaN')
        female_average_score = score_animeresponse_qs.filter(response__gender=Response.Gender.FEMALE).aggregate(Avg('score'))['score__avg'] or float('NaN')

        results_data = {
            ResultType.POPULARITY:                  div0(watcher_response_count, scaled_total_response_count),
            ResultType.POPULARITY_MALE:               male_popularity,
            ResultType.POPULARITY_FEMALE:           female_popularity,
            ResultType.GENDER_POPULARITY_RATIO:     div0(male_popularity, female_popularity),
            ResultType.UNDERWATCHED:                div0(watchers_animeresponse_qs.filter(underwatched=True).count(), watcher_response_count),
            ResultType.SCORE:                              average_score,
            ResultType.SCORE_MALE:                    male_average_score,
            ResultType.SCORE_FEMALE:                female_average_score,
            ResultType.GENDER_SCORE_DIFFERENCE:     male_average_score - female_average_score if min(male_average_score, female_average_score) > 0 else float('NaN'),
            ResultType.SURPRISE:                    div0(watchers_animeresponse_qs.filter(expectations=AnimeResponse.Expectations.SURPRISE      ).count(), watcher_response_count),
            ResultType.DISAPPOINTMENT:              div0(watchers_animeresponse_qs.filter(expectations=AnimeResponse.Expectations.DISAPPOINTMENT).count(), watcher_response_count),
            ResultType.AGE:                         watchers_animeresponse_qs.aggregate(avg_age=Avg('response__age'))['avg_age'] or float('NaN'),
        }
        return replace_nans(results_data)

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
    return a / b if b != 0 else float('NaN')

def replace_nans(val: Union[dict[Any, Any], list[Any], float, Any]) -> Any:
    if isinstance(val, dict):
        return { k: replace_nans(v) for k, v in val.items() }
    elif isinstance(val, list):
        return [replace_nans(v) for v in val]
    elif isinstance(val, float) and not math.isfinite(val):
        return None
    else:
        return val
