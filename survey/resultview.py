from django.views.generic import TemplateView
from django.db.models import Avg
from django.shortcuts import redirect
from django.core.cache import cache
from enum import Enum
from collections import OrderedDict
import inspect
from .models import Survey, AnimeResponse, Response, SurveyAdditionRemoval
from .util import SurveyUtil, get_username


class ResultsView(TemplateView):
    ANIME_POPULARITY_THRESHOLD = 2.0 # Anime below this percentage won't get included in results tables by default

    template_name = 'survey/results.html'
    model = Survey
    http_method_names = ['get']
    context_object_name = 'survey'

    def get_survey(self):
        return SurveyUtil.get_survey_or_404(
            year=self.kwargs['year'],
            season=self.kwargs['season'],
            pre_or_post=self.kwargs['pre_or_post'],
        )
    
    def get(self, request, *args, **kwargs):
        survey = self.get_survey()

        # Only display results if the survey is not ongoing, or if the user is staff
        if survey.is_ongoing and not request.user.is_staff:
            return redirect('survey:form', survey.year, survey.season, 'pre' if survey.is_preseason else 'post')
        else:
            return super().get(self, request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        survey = self.get_survey()

        results_generator = ResultsGenerator(survey)
        if survey.is_ongoing:
            anime_series_data, special_anime_data = results_generator.get_anime_results_data()
        else:
            anime_series_data, special_anime_data = cache.get_or_set('survey-%i' % survey.id, results_generator.get_anime_results_data, version=1)

        context['table_list'] = self.__generate_table_list(anime_series_data, special_anime_data, survey.is_preseason)
        context['username'] = get_username(self.request.user)
        return context
    

    def __generate_table_list(self, anime_series_data, special_anime_data, is_preseason):
        popularity_table = ResultsTable('Most Popular Anime', anime_series_data)
        popularity_table.generate([ResultsType.POPULARITY])
        
        gender_popularity_ratio_table = ResultsTable('Biggest Gender Popularity Disparity', anime_series_data)
        gender_popularity_ratio_table.generate([ResultsType.GENDER_POPULARITY_RATIO, ResultsType.POPULARITY])


        score_table = ResultsTable('Most Anticipated Anime' if is_preseason else 'Best Anime of the Season', anime_series_data)
        score_table.generate([ResultsType.SCORE])

        gender_score_difference_table = ResultsTable('Biggest Gender Score Disparity', anime_series_data)
        gender_score_difference_table.generate([ResultsType.GENDER_SCORE_DIFFERENCE, ResultsType.SCORE])
        
        special_popularity_table = ResultsTable('Most Popular Anime OVAs/ONAs/Movies/Specials', special_anime_data)
        special_popularity_table.generate([ResultsType.POPULARITY])

        if is_preseason:
            return [
                popularity_table, gender_popularity_ratio_table,
                score_table, gender_score_difference_table,
                special_popularity_table
            ]
        else:
            underwatched_table = ResultsTable('Most Underwatched Anime', anime_series_data)
            underwatched_table.generate([ResultsType.UNDERWATCHED, ResultsType.POPULARITY])

            surprise_table = ResultsTable('Most Surprising Anime', anime_series_data)
            surprise_table.generate([ResultsType.SURPRISE, ResultsType.SCORE])

            disappointment_table = ResultsTable('Most Disappointing Anime', anime_series_data)
            disappointment_table.generate([ResultsType.DISAPPOINTMENT, ResultsType.SCORE])

            special_score_table = ResultsTable('Most Anticipated Anime OVAs/ONAs/Movies/Specials' if is_preseason else 'Best Anime OVAs/ONAs/Movies/Specials', special_anime_data)
            special_score_table.generate([ResultsType.SCORE])

            return [
                popularity_table, gender_popularity_ratio_table, underwatched_table,
                score_table, gender_score_difference_table,
                surprise_table, disappointment_table,
                special_popularity_table, special_score_table
            ]
    


class ResultsGenerator:
    def __init__(self, survey):
        self.survey = survey

    def get_anime_results_data(self):
        if self.survey.is_ongoing:
            return self.__get_anime_results_data_internal()
        else:
            return cache.get_or_set('survey_results_%i' % self.survey.id, self.__get_anime_results_data_internal, version=1, timeout=60*30)

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

        responses_with_score = responses_for_anime.filter(score__isnull=False) if survey.is_preseason else responses_by_watchers.filter(score__isnull=False)
        # Becomes NaN if there are no scores (default behavior is None which causes errors, hence "or NaN" being necessary)
        male_average_score = responses_with_score.filter(response__gender=Response.Gender.MALE).aggregate(Avg('score'))['score__avg'] or float('NaN')
        female_average_score = responses_with_score.filter(response__gender=Response.Gender.FEMALE).aggregate(Avg('score'))['score__avg'] or float('NaN')

        return {
            ResultsType.POPULARITY:              watcher_count / adjusted_response_count * 100.0 if adjusted_response_count > 0 else float('NaN'),
            ResultsType.GENDER_POPULARITY_RATIO: (male_anime_response_count / male_response_count) / (female_anime_response_count / female_response_count) if female_anime_response_count > 0 else float('inf'),
            ResultsType.UNDERWATCHED:            responses_by_watchers.filter(underwatched=True).count() / watcher_count * 100.0 if watcher_count > 0 else float('NaN'),
            ResultsType.SCORE:                   responses_with_score.aggregate(Avg('score'))['score__avg'] or float('NaN'),
            ResultsType.GENDER_SCORE_DIFFERENCE: male_average_score - female_average_score if min(male_average_score, female_average_score) > 0 else float('NaN'),
            ResultsType.SURPRISE:                responses_by_watchers.filter(expectations=AnimeResponse.Expectations.SURPRISE).count() / watcher_count * 100.0 if watcher_count > 0 else float('NaN'),
            ResultsType.DISAPPOINTMENT:          responses_by_watchers.filter(expectations=AnimeResponse.Expectations.DISAPPOINTMENT).count() / watcher_count * 100.0 if watcher_count > 0 else float('NaN'),
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


class ResultsTable:
    ANIME_POPULARITY_THRESHOLD = 2.0 # Anime below this percentage won't get included in results tables by default

    def __init__(self, title, anime_data, ignore_anime_below_threshold=True):
        self.title = title
        self.anime_data = anime_data
        self.columns = []
        self.data = {}

        for anime in anime_data.keys():
            if ignore_anime_below_threshold and anime_data[anime][ResultsType.POPULARITY] < self.ANIME_POPULARITY_THRESHOLD:
                continue
            self.data[anime] = {}

    def generate(self, ordered_datatype_list, datatype_to_sort_by=None, is_descending=True, display_rank=True):
        self.__add_anime_column()

        for datatype in ordered_datatype_list:
            for anime in self.data.keys():
                self.data[anime][datatype.name] = self.anime_data[anime][datatype]
            self.columns.append(ResultsTable.Column(
                key=datatype.name,
                label=datatype.value,
                formatter=datatype.get_formatter_name(),
                td_class='text-right',
                th_class='text-right',
            ))

        if datatype_to_sort_by is None:
            datatype_to_sort_by = ordered_datatype_list[0]
        self.__sort(datatype_to_sort_by, is_descending, display_rank)

    def __add_anime_column(self):
        datatype = ResultsType.NAME

        for anime in self.data.keys():
            self.data[anime][datatype.name] = str(anime)
        self.columns.append(ResultsTable.Column(
            key=datatype.name,
            label=datatype.value,
        ))

    def __add_rank_column(self):
        i = 1
        for _, row in self.data.items():
            row['rank'] = i
            i += 1
        
        self.columns.insert(0, ResultsTable.Column(
            key='rank',
            label='#'
        ))

    def __sort(self, datatype_to_sort_by, is_descending, display_rank):
        def get_sort_key(item):
            value = item[1][datatype_to_sort_by.name]
            if value == float('inf') or value != value:
                return float('-inf')
            else:
                return value

        self.data = OrderedDict(sorted(
            self.data.items(),
            key=get_sort_key,
            reverse=is_descending,
        ))

        if display_rank:
            self.__add_rank_column()


    class Column:
        def __init__(self, key, label, formatter=None, td_class='', th_class=''):
            self.key = key
            self.label = label
            self.formatter = formatter
            self.tdClass = td_class
            self.thClass = th_class
        
        def as_keyvalue(self):
            attributes = inspect.getmembers(self, lambda member: not inspect.isroutine(member))
            return [attribute for attribute in attributes if attribute[1] and not attribute[0].startswith('__')]


class ResultsType(Enum):
    POPULARITY              = "Popularity"
    GENDER_POPULARITY_RATIO = "Gender Ratio (♂:♀)"
    UNDERWATCHED            = "Underwatched"
    SCORE                   = "Score"
    GENDER_SCORE_DIFFERENCE = "Gender Score Difference (♂-♀)"
    SURPRISE                = "Surprise"
    DISAPPOINTMENT          = "Disappointment"
    NAME                    = "Anime" # Only used to be able to sort by this column

    def get_formatter_name(self):
        if self is ResultsType.GENDER_POPULARITY_RATIO:
            return 'genderRatioFormatter'
        elif self is ResultsType.SCORE or self is ResultsType.GENDER_SCORE_DIFFERENCE:
            return 'scoreFormatter'
        else:
            return 'percentageFormatter'
