from collections import OrderedDict
from django.views.generic import TemplateView
from django.db.models import Avg, Q
from django.shortcuts import redirect
from django.core.cache import caches
from enum import Enum, auto
import json
from survey.models import AnimeResponse, Response, Survey, SurveyAdditionRemoval
from survey.util import SurveyUtil, AnimeUtil
from .mixins import SurveyMixin, UserMixin

#region Views
class BaseResultsView(UserMixin, SurveyMixin, TemplateView):
    """Base class for views displaying survey results."""
    def get(self, request, *args, **kwargs):
        survey = self.get_survey()

        # Only display results if the survey is not ongoing, or if the user is staff
        if survey.state != Survey.State.FINISHED and not request.user.is_staff:
            return redirect('survey:form', survey.year, survey.season, 'pre' if survey.is_preseason else 'post')
        else:
            return super().get(self, request, *args, **kwargs)


class FullResultsView(BaseResultsView):
    """Class-based results view containing a table with all the results of a survey."""
    template_name = 'survey/fullresults.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        survey = self.get_survey()

        results_generator = ResultsGenerator(survey)
        context['anime_info_json'], context['anime_series_data_json'], context['special_anime_data_json'] = results_generator.get_anime_results_data_json()
        context['sort_by'] = self.request.GET.get('sort', default='name')

        return context


class ResultsView(BaseResultsView):
    """Class-based results view."""
    template_name = 'survey/results.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        survey = self.get_survey()

        results_generator = ResultsGenerator(survey)
        context['anime_info_json'], context['anime_series_data_json'], context['special_anime_data_json'] = results_generator.get_anime_results_data_json()
        context['root_item'] = self.__get_segments()

        survey_responses = Response.objects.filter(survey=survey)
        response_count = survey_responses.count()
        context['response_count'] = response_count
        context['average_age'] = survey_responses.aggregate(avg_age=Avg('age'))['avg_age'] or float('NaN')

        context['gender_distribution'] = self.__get_gender_distribution(survey_responses)

        age_distribution = self.__get_age_distribution(survey_responses)
        context['age_distribution'] = age_distribution
        context['age_distribution_max'] = max(age_distribution.values())
        return context

    def __get_segments(self):
        survey = self.get_survey()

        # For segments that are post-season survey exclusive
        _ = lambda segment: EmptySegment() if survey.is_preseason else segment

        root_item = SegmentGroup('', is_root=True, children=[
            SegmentGroup('Popularity', [
                TableWithTop3Segment('Most Popular Anime Series', ResultsType.POPULARITY, top_count=10),
                HiddenSegmentGroup('Popularity - By Gender', [
                    TablePairSegment('Most Popular Anime by Gender', ResultsType.POPULARITY_MALE, ResultsType.POPULARITY_FEMALE, ResultsType.POPULARITY, row_count=5),
                    TablePairSegment('Biggest Differences in Popularity by Gender', ResultsType.GENDER_POPULARITY_RATIO, extra_result_type=ResultsType.POPULARITY, row_count=3, description="Expressed as the ratio of male popularity to female popularity (and vice versa)."),
                ]),
                HiddenSegmentGroup('Popularity - Miscellaneous', [
                    _(TableWithTop3Segment('Most Underwatched Anime', ResultsType.UNDERWATCHED, ResultsType.POPULARITY, top_count=5)),
                    TablePairSegment('Average Age per Anime', ResultsType.AGE, row_count=3),
                ]),
            ]),
            SegmentGroup('Impressions', [
                TableWithTop3Segment(('Most (and Least) Anticipated' if survey.is_preseason else 'Best (and Worst)') + ' Anime of the Season', ResultsType.SCORE, top_count=10, bottom_count=5),
                HiddenSegmentGroup('Impressions - By Gender', [
                    TablePairSegment(('Most Anticipated' if survey.is_preseason else 'Best') + ' Anime of the Season by Gender', ResultsType.SCORE_MALE, ResultsType.SCORE_FEMALE, ResultsType.SCORE, row_count=5),
                    TablePairSegment('Biggest Differences in Score by Gender', ResultsType.GENDER_SCORE_DIFFERENCE, extra_result_type=ResultsType.SCORE, row_count=3, description="Expressed in how much higher an anime was scored by men compared to women (and vice versa)."),
                ]),
                HiddenSegmentGroup('Impressions - Expectations', [
                    _(TableWithTop3Segment('Most Surprising Anime', ResultsType.SURPRISE, ResultsType.SCORE, top_count=5)),
                    _(TableWithTop3Segment('Most Disappointing Anime', ResultsType.DISAPPOINTMENT, ResultsType.SCORE, top_count=5)),
                ]),
            ]),
            SegmentGroup('Anime OVAs / ONAs / Movies / Specials', [
                TableWithTop3Segment('Most Popular Anime OVAs / ONAs / Movies / Specials', ResultsType.POPULARITY, is_for_series=False, top_count=5),
                _(TableWithTop3Segment('Most Anticipated Anime OVAs / ONAs / Movies / Specials' if survey.is_preseason else 'Best Anime OVAs / ONAs / Movies / Specials', ResultsType.SCORE, is_for_series=False, top_count=5)),
            ]),
        ])

        return root_item

    def __get_gender_distribution(self, survey_responses):
        gender_answers_queryset = survey_responses.filter(~Q(gender=''), gender__isnull=False)
        gender_answers_count = len(gender_answers_queryset)
        gender_distribution = OrderedDict([
            (Response.Gender.MALE,   gender_answers_queryset.filter(gender=Response.Gender.MALE  ).count() / max(gender_answers_count, 1) * 100),
            (Response.Gender.FEMALE, gender_answers_queryset.filter(gender=Response.Gender.FEMALE).count() / max(gender_answers_count, 1) * 100),
            (Response.Gender.OTHER,  gender_answers_queryset.filter(gender=Response.Gender.OTHER ).count() / max(gender_answers_count, 1) * 100),
        ])

        return gender_distribution

    def __get_age_distribution(self, survey_responses):
        age_distribution = [0]*81
        age_list = survey_responses.filter(age__isnull=False, age__gt=0).values_list('age', flat=True)
        age_count = len(age_list)

        # Count for each age how many people are that old.
        for age in age_list:
            if age > 0 and age <= 80:
                age_distribution[int(age)] += 1

        # Normalize the values to 0-100.
        for i in range(len(age_distribution)):
            age_distribution[i] /= max(age_count, 1) / 100.0

        # Convert the list to a dict.
        age_distribution = OrderedDict([
            (idx, age_distribution[idx]) for idx in range(5, 81)
        ])

        return age_distribution
#endregion


#region Segments
class SegmentType(Enum):
    EMPTY = auto()
    GROUP = auto()
    HIDDEN_GROUP = auto()
    TABLE_WITH_TOP3 = auto()
    TABLE_PAIR = auto()

class Segment:
    def __init__(self, item_type, title):
        self.item_type = item_type
        self.title = title
    
    def _set_id(self, item_id):
        self.id = item_id
        return item_id + 1


class EmptySegment(Segment):
    def __init__(self):
        super().__init__(SegmentType.EMPTY, None)

class SegmentGroup(Segment):
    def __init__(self, title, children=[], is_root=False, item_type=SegmentType.GROUP):
        super().__init__(item_type, title)
        self.children = children
        if is_root:
            self._set_id(0)
    
    def _set_id(self, start_item_id):
        next_id = super()._set_id(start_item_id)
        for child in self.children:
            next_id = child._set_id(next_id)
        return next_id

class HiddenSegmentGroup(SegmentGroup):
    def __init__(self, title, children=[], is_root=False):
        super().__init__(title, children, is_root, SegmentType.HIDDEN_GROUP)


class TableBaseSegment(Segment):
    def __init__(self, item_type, title, main_result_type, inverse_result_type=None, extra_result_type=None, description=None, is_for_series=True, top_count=None, bottom_count=None):
        super().__init__(item_type, title)

        self.is_for_series = is_for_series
        self.main_result_type = main_result_type
        self.inverse_result_type = inverse_result_type
        self.extra_result_type = extra_result_type
        self.top_count = top_count
        self.bottom_count = bottom_count
        self.description = description


class TableWithTop3Segment(TableBaseSegment):
    def __init__(self, title, main_result_type, extra_result_type=None, description=None, is_for_series=True, top_count=None, bottom_count=None):
        super().__init__(SegmentType.TABLE_WITH_TOP3, title, main_result_type, None, extra_result_type, description, is_for_series, top_count, bottom_count)


class TablePairSegment(TableBaseSegment):
    def __init__(self, title, main_result_type, inverse_result_type=None, extra_result_type=None, description=None, is_for_series=True, row_count=None):
        super().__init__(SegmentType.TABLE_PAIR, title, main_result_type, inverse_result_type, extra_result_type, description, is_for_series, row_count)
#endregion


class ResultsGenerator:
    """Class for generating survey results."""

    def __init__(self, survey):
        """Creates a survey results generator.

        Parameters
        ----------
        survey : Survey
            The survey for which results have to be generated.
        """
        self.survey = survey

    def get_anime_results_data_json(self):
        anime_series_data, special_anime_data = self.get_anime_results_data()

        anime_info_json = json.JSONEncoder().encode({
            anime.id: {
                'official_name_list': AnimeUtil.get_name_list(anime),
                'type': anime.anime_type,
                'image_list': AnimeUtil.get_image_url_list(anime),
            } for anime in list(anime_series_data.keys()) + list(special_anime_data.keys())
        })

        def __convert_data(anime_data):
            return json.JSONEncoder().encode({
                anime.id: {
                    results_type.name.lower(): value for results_type, value in results.items()
                } for anime, results in anime_data.items()
            })

        return anime_info_json, __convert_data(anime_series_data), __convert_data(special_anime_data)

    def get_anime_results_data(self):
        """Obtains the results for the survey provided when initializing, either from the cache or generated from database data.

        Returns
        -------
        ({Anime: {ResultsType: any}}, {Anime: {ResultsType: any}})
            A dict for anime series and one for special anime, where each anime has an associated dict of result values.
        """
        if self.survey.state != Survey.State.FINISHED:
            return self.__get_anime_results_data_internal()
        else:
            cache_timeout = SurveyUtil.get_survey_cache_timeout(self.survey)
            return caches['long'].get_or_set('survey_results_%i' % self.survey.id, self.__get_anime_results_data_internal, version=3, timeout=cache_timeout)

    # Please refactor this sometime
    def __get_anime_results_data_internal(self):
        survey = self.survey

        _, anime_series_list, special_anime_list = SurveyUtil.get_survey_anime(survey)
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
    def __get_data_for_anime(self, anime, animeresponse_queryset, surveyadditionsremovals_queryset, total_response_count, total_male_response_count, total_female_response_count):
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

    def __get_adjusted_response_count(self, addition_removal_list, response_count):
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

    def get_formatter_name(self):
        ratio_formatter_types = [ResultsType.GENDER_POPULARITY_RATIO, ResultsType.GENDER_POPULARITY_RATIO_INV]
        score_formatter_types = [
            ResultsType.SCORE, ResultsType.SCORE_MALE, ResultsType.SCORE_FEMALE,
            ResultsType.GENDER_SCORE_DIFFERENCE, ResultsType.GENDER_SCORE_DIFFERENCE_INV,
            ResultsType.AGE,
        ]

        if self in ratio_formatter_types:
            return 'genderRatioFormatter'
        elif self in score_formatter_types:
            return 'scoreFormatter'
        else:
            return 'percentageFormatter'


def div0(a: float, b: float):
    return a / b if b > 0 else float('NaN')
