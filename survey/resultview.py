from django.views.generic import TemplateView, DetailView
from django.db.models import Avg, Q
from django.shortcuts import redirect
from django.core.cache import cache, caches
from enum import Enum, auto
from collections import OrderedDict
import inspect
import json
from .models import Survey, AnimeResponse, Response, SurveyAdditionRemoval, AnimeName
from .util import SurveyUtil, get_user_info, AnimeUtil

ANIME_POPULARITY_THRESHOLD = 0.02 # Anime with a popularity lower than this won't get included in results tables by default

#region Views
class BaseResultsView(TemplateView):
    """Base class for views displaying survey results."""
    http_method_names = ['get']
    
    def get(self, request, *args, **kwargs):
        survey = self._get_survey()

        # Only display results if the survey is not ongoing, or if the user is staff
        if survey.is_ongoing and not request.user.is_staff:
            return redirect('survey:form', survey.year, survey.season, 'pre' if survey.is_preseason else 'post')
        else:
            return super().get(self, request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        survey = self._get_survey()

        context['survey'] = survey
        context['user_info'] = get_user_info(self.request.user)

        return context

    def _get_survey(self):
        return SurveyUtil.get_survey_or_404(
            year=self.kwargs['year'],
            season=self.kwargs['season'],
            pre_or_post=self.kwargs['pre_or_post'],
        )


class FullResultsView(BaseResultsView):
    """Class-based results view containing a table with all the results of a survey."""
    template_name = 'survey/fullresults.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        survey = self._get_survey()

        results_generator = ResultsGenerator(survey)
        context['anime_info_json'], context['anime_series_data_json'], context['special_anime_data_json'] = results_generator.get_anime_results_data_json()
        context['sort_by'] = self.request.GET.get('sort', default='name')

        return context


class ResultsView(BaseResultsView):
    """Class-based results view."""
    template_name = 'survey/results.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        survey = self._get_survey()

        results_generator = ResultsGenerator(survey)


        context['anime_info_json'], context['anime_series_data_json'], context['special_anime_data_json'] = results_generator.get_anime_results_data_json()
        context['root_item'] = SegmentGroup(is_root=True, title='', children=[
            SegmentGroup('Popularity', [
                TableWithTop3Segment('Most Popular Anime Series', ResultsType.POPULARITY, top_count=10),
                TablePairSegment('Biggest Differences in Popularity by Gender', ResultsType.GENDER_POPULARITY_RATIO, ResultsType.POPULARITY, row_count=3, description="Expressed as the ratio of male popularity to female popularity (and vice versa)."),
                SegmentGroup('Popularity - Miscellaneous', [
                    EmptySegment() if survey.is_preseason else TableWithTop3Segment('Most Underwatched Anime', ResultsType.UNDERWATCHED, ResultsType.POPULARITY, top_count=5),
                    TablePairSegment('Average Age per Anime', ResultsType.AGE, row_count=3),
                ]),
            ]),
            SegmentGroup('Impressions', [
                TableWithTop3Segment(('Most (and Least) Anticipated' if survey.is_preseason else 'Best (and Worst)') + ' Anime of the Season', ResultsType.SCORE, top_count=10, bottom_count=5),
                TablePairSegment('Biggest Differences in Score by Gender', ResultsType.GENDER_SCORE_DIFFERENCE, ResultsType.SCORE, row_count=3, description="Expressed in how much higher an anime was scored by men compared to women (and vice versa)."),
                EmptySegment() if survey.is_preseason else TableWithTop3Segment('Most Surprising Anime', ResultsType.SURPRISE, ResultsType.SCORE, top_count=5),
                EmptySegment() if survey.is_preseason else TableWithTop3Segment('Most Disappointing Anime', ResultsType.DISAPPOINTMENT, ResultsType.SCORE, top_count=5),
            ]),
            SegmentGroup('Anime OVAs / ONAs / Movies / Specials', [
                TableWithTop3Segment('Most Popular Anime OVAs / ONAs / Movies / Specials', ResultsType.POPULARITY, is_for_series=False, top_count=5),
                EmptySegment() if survey.is_preseason else TableWithTop3Segment('Most Anticipated Anime OVAs / ONAs / Movies / Specials' if survey.is_preseason else 'Best Anime OVAs / ONAs / Movies / Specials', ResultsType.SCORE, is_for_series=False, top_count=5),
            ]),
        ])

        survey_responses = Response.objects.filter(survey=survey)
        response_count = survey_responses.count()
        context['response_count'] = response_count
        context['average_age'] = survey_responses.aggregate(avg_age=Avg('age'))['avg_age'] or float('NaN')

        gender_answers_queryset = survey_responses.filter(~Q(gender=''), gender__isnull=False)
        gender_answers_count = len(gender_answers_queryset)
        context['gender_distribution'] = OrderedDict([
            (Response.Gender.MALE,   gender_answers_queryset.filter(gender=Response.Gender.MALE  ).count() / max(gender_answers_count, 1) * 100),
            (Response.Gender.FEMALE, gender_answers_queryset.filter(gender=Response.Gender.FEMALE).count() / max(gender_answers_count, 1) * 100),
            (Response.Gender.OTHER,  gender_answers_queryset.filter(gender=Response.Gender.OTHER ).count() / max(gender_answers_count, 1) * 100),
        ])


        age_distribution = [0]*81
        age_list = survey_responses.filter(age__isnull=False, age__gt=0).values_list('age', flat=True)
        age_count = len(age_list)
        age_max = 0

        # Count for each age how many people are that old.
        for age in age_list:
            if age > 0 and age <= 80:
                age_distribution[int(age)] += 1

        # Normalize the values.
        for i in range(len(age_distribution)):
            age_distribution[i] /= max(age_count, 1) / 100.0
            if age_distribution[i] > age_max:
                age_max = age_distribution[i]

        # Convert the list to a dict.
        age_distribution = OrderedDict([
            (idx, age_distribution[idx]) for idx in range(5, 81)
        ])
            
        context['age_distribution'] = age_distribution
        context['age_distribution_max'] = age_max
        return context
#endregion


class SegmentType(Enum):
    EMPTY = auto()
    GROUP = auto()
    TABLE_WITH_TOP3 = auto()
    TABLE_PAIR = auto()

class Segment:
    def __init__(self, item_type, title):
        self.item_type = item_type
        self.title = title
    
    def set_id(self, item_id):
        self.id = item_id
        return item_id + 1


class EmptySegment(Segment):
    def __init__(self):
        super().__init__(SegmentType.EMPTY, None)

class SegmentGroup(Segment):
    def __init__(self, title, children=[], is_root=False):
        super().__init__(SegmentType.GROUP, title)

        self.children = children

        if is_root:
            self.set_id(0)
    
    def set_id(self, start_item_id):
        next_id = super().set_id(start_item_id)
        for child in self.children:
            next_id = child.set_id(next_id)
        return next_id



class TableBaseSegment(Segment):
    def __init__(self, item_type, title, main_result_type, extra_result_type=None, description=None, is_for_series=True, top_count=None, bottom_count=None):
        super().__init__(item_type, title)

        self.is_for_series = is_for_series
        self.main_result_type = main_result_type
        self.extra_result_type = extra_result_type
        self.top_count = top_count
        self.bottom_count = bottom_count
        self.description = description


class TableWithTop3Segment(TableBaseSegment):
    def __init__(self, title, main_result_type, extra_result_type=None, description=None, is_for_series=True, top_count=None, bottom_count=None):
        super().__init__(SegmentType.TABLE_WITH_TOP3, title, main_result_type, extra_result_type, description, is_for_series, top_count, bottom_count)


class TablePairSegment(TableBaseSegment):
    def __init__(self, title, main_result_type, extra_result_type=None, description=None, is_for_series=True, row_count=None):
        super().__init__(SegmentType.TABLE_PAIR, title, main_result_type, extra_result_type, description, is_for_series, row_count)


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
                'image': {
                    's': AnimeUtil.get_anime_image_url(anime, variant='s'),
                    'm': AnimeUtil.get_anime_image_url(anime, variant='m'),
                    'l': AnimeUtil.get_anime_image_url(anime, variant='l'),
                },
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
        if self.survey.is_ongoing:
            return self.__get_anime_results_data_internal()
        else:
            cache_timeout = SurveyUtil.get_survey_cache_timeout(self.survey)
            return caches['long'].get_or_set('survey_results_%i' % self.survey.id, self.__get_anime_results_data_internal, version=1, timeout=cache_timeout)

    # Please refactor this sometime
    def __get_anime_results_data_internal(self):
        survey = self.survey

        _, anime_series_list, special_anime_list = SurveyUtil.get_survey_anime(survey)
        animeresponse_queryset = AnimeResponse.objects.filter(response__survey=survey)
        surveyadditionsremovals_queryset = SurveyAdditionRemoval.objects.filter(survey=survey)

        response_count = Response.objects.filter(survey=survey).count()
        male_response_count = Response.objects.filter(survey=survey, gender=Response.Gender.MALE).count()
        female_response_count = Response.objects.filter(survey=survey, gender=Response.Gender.FEMALE).count()

        # Get a dict of data values for each anime (i.e. a dict with for each anime a dict with data values, dict[anime][data])
        anime_series_data = {
            anime: self.__get_data_for_anime(anime, animeresponse_queryset, surveyadditionsremovals_queryset, response_count, male_response_count, female_response_count) for anime in anime_series_list
        }
        special_anime_data = {
            anime: self.__get_data_for_anime(anime, animeresponse_queryset, surveyadditionsremovals_queryset, response_count, male_response_count, female_response_count) for anime in special_anime_list
        }
        return anime_series_data, special_anime_data

    # Returns a dict of data values for an anime
    def __get_data_for_anime(self, anime, animeresponse_queryset, surveyadditionsremovals_queryset, response_count, male_response_count, female_response_count):
        survey = self.survey

        responses_for_anime = animeresponse_queryset.filter(anime=anime)
        responses_by_watchers = responses_for_anime.filter(watching=True)

        # Adjust response count for this anime taking into account the times the anime was added/removed to the survey
        addition_removal_list = list(surveyadditionsremovals_queryset.filter(anime=anime))
        adjusted_response_count = self.__get_adjusted_response_count(addition_removal_list, response_count)

        # Amount of people watching
        watcher_count = responses_by_watchers.count()
        male_anime_response_count = responses_by_watchers.filter(response__gender=Response.Gender.MALE).count()
        female_anime_response_count = responses_by_watchers.filter(response__gender=Response.Gender.FEMALE).count()

        male_popularity = male_anime_response_count / male_response_count if male_response_count > 0 else float('NaN')
        female_popularity = female_anime_response_count / female_response_count if female_response_count > 0 else float('NaN')
        gender_popularity_ratio = male_popularity / female_popularity if female_popularity > 0 else float('inf')
        gender_popularity_ratio_inv = female_popularity / male_popularity if male_anime_response_count > 0 else float('inf')

        responses_with_score = responses_for_anime.filter(score__isnull=False) if survey.is_preseason else responses_by_watchers.filter(score__isnull=False)
        # Becomes NaN if there are no scores (default behavior is None which causes errors, hence "or NaN" being necessary)
        male_average_score = responses_with_score.filter(response__gender=Response.Gender.MALE).aggregate(Avg('score'))['score__avg'] or float('NaN')
        female_average_score = responses_with_score.filter(response__gender=Response.Gender.FEMALE).aggregate(Avg('score'))['score__avg'] or float('NaN')

        return {
            ResultsType.POPULARITY:              watcher_count / adjusted_response_count * 100.0 if adjusted_response_count > 0 else float('NaN'),
            ResultsType.GENDER_POPULARITY_RATIO: gender_popularity_ratio,
            ResultsType.GENDER_POPULARITY_RATIO_INV: gender_popularity_ratio_inv,
            ResultsType.UNDERWATCHED:            responses_by_watchers.filter(underwatched=True).count() / watcher_count * 100.0 if watcher_count > 0 else float('NaN'),
            ResultsType.SCORE:                   responses_with_score.aggregate(Avg('score'))['score__avg'] or float('NaN'),
            ResultsType.GENDER_SCORE_DIFFERENCE: male_average_score - female_average_score if min(male_average_score, female_average_score) > 0 else float('NaN'),
            ResultsType.GENDER_SCORE_DIFFERENCE_INV: female_average_score - male_average_score if min(male_average_score, female_average_score) > 0 else float('NaN'),
            ResultsType.SURPRISE:                responses_by_watchers.filter(expectations=AnimeResponse.Expectations.SURPRISE).count() / watcher_count * 100.0 if watcher_count > 0 else float('NaN'),
            ResultsType.DISAPPOINTMENT:          responses_by_watchers.filter(expectations=AnimeResponse.Expectations.DISAPPOINTMENT).count() / watcher_count * 100.0 if watcher_count > 0 else float('NaN'),
            ResultsType.AGE:                     responses_by_watchers.aggregate(avg_age=Avg('response__age'))['avg_age'] or float('NaN'),
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
    POPULARITY              = "Popularity"
    GENDER_POPULARITY_RATIO = "Gender Ratio (♂:♀)"
    GENDER_POPULARITY_RATIO_INV = "Gender Ratio (♀:♂)"
    UNDERWATCHED            = "Underwatched"
    SCORE                   = "Score"
    GENDER_SCORE_DIFFERENCE = "Gender Score Difference (♂-♀)"
    GENDER_SCORE_DIFFERENCE_INV = "Gender Score Difference (♀-♂)"
    SURPRISE                = "Surprise"
    DISAPPOINTMENT          = "Disappointment"
    AGE                     = "Average Viewer Age"
    NAME                    = "Anime" # Only used to be able to sort by this column

    def get_formatter_name(self):
        if self is ResultsType.GENDER_POPULARITY_RATIO or self is ResultsType.GENDER_POPULARITY_RATIO_INV:
            return 'genderRatioFormatter'
        elif self is ResultsType.SCORE or self is ResultsType.GENDER_SCORE_DIFFERENCE or self is ResultsType.GENDER_SCORE_DIFFERENCE_INV or self is ResultsType.AGE:
            return 'scoreFormatter'
        else:
            return 'percentageFormatter'
