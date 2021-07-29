from collections import OrderedDict
from django.views.generic import TemplateView
from django.db.models import Avg, Q
from django.shortcuts import redirect
from enum import Enum, auto
from survey.models import Response, Survey
from survey.util.results import ResultsGenerator, ResultsType
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
