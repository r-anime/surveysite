from django.views.generic import TemplateView
from django.db.models import Avg
from django.shortcuts import redirect
from enum import Enum
from .models import Survey, AnimeResponse, Response, SurveyAdditionRemoval
from .views import get_survey_or_404, get_username, get_survey_anime


class ResultsView(TemplateView):
    ANIME_POPULARITY_THRESHOLD = 2.0 # Anime below this percentage won't get included in results tables by default

    template_name = 'survey/results.html'
    model = Survey
    http_method_names = ['get']
    context_object_name = 'survey'

    def get_object(self):
        return get_survey_or_404(
            year=self.kwargs['year'],
            season=self.kwargs['season'],
            pre_or_post=self.kwargs['pre_or_post'],
        )
    
    def get(self, request, *args, **kwargs):
        survey = self.get_object()

        # Only display results if the survey is not ongoing, or if the user is staff
        if survey.is_ongoing and not request.user.is_staff:
            return redirect('survey:form', survey.year, survey.season, 'pre' if survey.is_preseason else 'post')
        else:
            return super().get(self, request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        survey = self.get_object()

        _, anime_series_list, special_anime_list = get_survey_anime(survey)
        animeresponse_queryset = AnimeResponse.objects.filter(response__survey=survey)
        surveyadditionsremovals_queryset = SurveyAdditionRemoval.objects.filter(survey=survey)

        response_count = Response.objects.filter(survey=survey).count()
        male_response_count = Response.objects.filter(survey=survey, gender=Response.Gender.MALE).count()
        female_response_count = Response.objects.filter(survey=survey, gender=Response.Gender.FEMALE).count()

        # Get a dict of data values for each anime (i.e. a dict with for each anime a dict with data values, dict[anime][data])
        anime_series_data = {
            anime: self.get_data_for_anime(survey, anime, animeresponse_queryset, surveyadditionsremovals_queryset, response_count, male_response_count, female_response_count) for anime in anime_series_list
        }
        special_anime_data = {
            anime: self.get_data_for_anime(survey, anime, animeresponse_queryset, surveyadditionsremovals_queryset, response_count, male_response_count, female_response_count) for anime in special_anime_list
        }

        popularity_table = self.generate_table(
            anime_series_data,
            'Most Popular Anime',
            [ResultsView.DataType.POPULARITY],
        )
        gender_popularity_ratio_table = self.generate_table(
            anime_series_data,
            'Biggest Gender Popularity Disparity',
            [ResultsView.DataType.GENDER_POPULARITY_RATIO, ResultsView.DataType.POPULARITY],
        )
        underwatched_table = self.generate_table(
            anime_series_data,
            'Most Underwatched Anime',
            [ResultsView.DataType.UNDERWATCHED, ResultsView.DataType.POPULARITY],
        )

        score_table = self.generate_table(
            anime_series_data,
            'Most Anticipated Anime' if survey.is_preseason else 'Best Anime of the Season',
            [ResultsView.DataType.SCORE],
        )
        gender_score_difference_table = self.generate_table(
            anime_series_data,
            'Biggest Gender Score Disparity',
            [ResultsView.DataType.GENDER_SCORE_DIFFERENCE, ResultsView.DataType.SCORE],
        )

        surprise_table = self.generate_table(
            anime_series_data,
            'Most Surprising Anime',
            [ResultsView.DataType.SURPRISE, ResultsView.DataType.SCORE],
        )
        disappointment_table = self.generate_table(
            anime_series_data,
            'Most Disappointing Anime',
            [ResultsView.DataType.DISAPPOINTMENT, ResultsView.DataType.SCORE],
        )
        
        special_popularity_table = self.generate_table(
            special_anime_data,
            'Most Popular Anime OVAs/ONAs/Movies/Specials',
            [ResultsView.DataType.POPULARITY],
        )
        special_score_table = self.generate_table(
            special_anime_data,
            'Most Anticipated Anime OVAs/ONAs/Movies/Specials' if survey.is_preseason else 'Best Anime OVAs/ONAs/Movies/Specials',
            [ResultsView.DataType.SCORE],
        )

        if survey.is_preseason:
            table_list = [
                popularity_table, gender_popularity_ratio_table,
                score_table, gender_score_difference_table,
                special_popularity_table
            ]
        else:
            table_list = [
                popularity_table, gender_popularity_ratio_table, underwatched_table,
                score_table, gender_score_difference_table,
                surprise_table, disappointment_table,
                special_popularity_table, special_score_table
            ]

        context['table_list'] = table_list
        context['username'] = get_username(self.request.user)
        return context
    




    def get_adjusted_response_count(self, addition_removal_list, response_count):
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

    # Returns a dict of data values for an anime
    def get_data_for_anime(self, survey, anime, animeresponse_queryset, surveyadditionsremovals_queryset, response_count, male_response_count, female_response_count):
        responses_for_anime = animeresponse_queryset.filter(anime=anime)
        responses_by_watchers = responses_for_anime.filter(watching=True)

        # Adjust response count for this anime taking into account the times the anime was added/removed to the survey
        addition_removal_list = list(surveyadditionsremovals_queryset.filter(anime=anime))
        adjusted_response_count = self.get_adjusted_response_count(addition_removal_list, response_count)

        # Amount of people watching
        watcher_count = responses_by_watchers.count()
        male_anime_response_count = responses_by_watchers.filter(response__gender=Response.Gender.MALE).count()
        female_anime_response_count = responses_by_watchers.filter(response__gender=Response.Gender.FEMALE).count()

        responses_with_score = responses_for_anime.filter(score__isnull=False) if survey.is_preseason else responses_by_watchers.filter(score__isnull=False)
        # Becomes NaN if there are no scores (default behavior is None which causes errors, hence "or NaN" being necessary)
        male_average_score = responses_with_score.filter(response__gender=Response.Gender.MALE).aggregate(Avg('score'))['score__avg'] or float('NaN')
        female_average_score = responses_with_score.filter(response__gender=Response.Gender.FEMALE).aggregate(Avg('score'))['score__avg'] or float('NaN')

        return {
            ResultsView.DataType.POPULARITY:              watcher_count / adjusted_response_count * 100.0 if adjusted_response_count > 0 else float('NaN'),
            ResultsView.DataType.GENDER_POPULARITY_RATIO: (male_anime_response_count / male_response_count) / (female_anime_response_count / female_response_count) if female_anime_response_count > 0 else float('inf'),
            ResultsView.DataType.UNDERWATCHED:            responses_by_watchers.filter(underwatched=True).count() / watcher_count * 100.0 if watcher_count > 0 else float('NaN'),
            ResultsView.DataType.SCORE:                   responses_with_score.aggregate(Avg('score'))['score__avg'] or float('NaN'),
            ResultsView.DataType.GENDER_SCORE_DIFFERENCE: male_average_score - female_average_score if min(male_average_score, female_average_score) > 0 else float('NaN'),
            ResultsView.DataType.SURPRISE:                responses_by_watchers.filter(expectations=AnimeResponse.Expectations.SURPRISE).count() / watcher_count * 100.0 if watcher_count > 0 else float('NaN'),
            ResultsView.DataType.DISAPPOINTMENT:          responses_by_watchers.filter(expectations=AnimeResponse.Expectations.DISAPPOINTMENT).count() / watcher_count * 100.0 if watcher_count > 0 else float('NaN'),
        }


    # Generate table data as a list of rows
    def generate_table_data(self, anime_data, data_types_to_display, ignore_below_threshold):
        table_data = []

        for anime in anime_data.keys():
            if ignore_below_threshold and anime_data[anime][ResultsView.DataType.POPULARITY] < self.ANIME_POPULARITY_THRESHOLD:
                continue

            row = {"anime": str(anime)}
            for data_type in data_types_to_display:
                row[data_type.name] = anime_data[anime][data_type]
            table_data.append(row)
    
        return table_data
    
    def generate_table(self, anime_data, table_name, data_types_to_display, data_type_to_sort_by=None, reverse_sort=True, ignore_below_threshold=True):
        if not data_type_to_sort_by:
            data_type_to_sort_by = data_types_to_display[0]
        
        table = {
            'title': table_name,
            'data': None,
            'columns': None,
        }

        table_data = self.generate_table_data(anime_data, data_types_to_display, ignore_below_threshold)
        
        table_data.sort(
            key=lambda row: float('-inf') if row[data_type_to_sort_by.name] == float('inf') or row[data_type_to_sort_by.name] != row[data_type_to_sort_by.name] else row[data_type_to_sort_by.name],
            reverse=reverse_sort
        )
        for i in range(len(table_data)):
            table_data[i]['rank'] = i+1
        
        table['data'] = table_data
        table['columns'] = [{
                'key': data_type.name,
                'label': data_type.value,
                #'sortable': True,
                'formatter': data_type.get_formatter(),
                'tdClass': 'text-right',
                'thClass': 'text-right',
            } for data_type in data_types_to_display
        ]
        table['columns'] = [{
                'key': 'rank',
                'label': '#',
                #'sortable': True,
            }, {
                'key': 'anime',
                'label': 'Anime',
                #'sortable': True,
            }
        ] + table['columns']
            
        return table
    

    class DataType(Enum):
        POPULARITY              = "Popularity"
        GENDER_POPULARITY_RATIO = "Gender Ratio (♂:♀)"
        UNDERWATCHED            = "Underwatched"
        SCORE                   = "Score"
        GENDER_SCORE_DIFFERENCE = "Gender Score Difference (♂-♀)"
        SURPRISE                = "Surprise"
        DISAPPOINTMENT          = "Disappointment"

        def get_formatter(self):
            if self is ResultsView.DataType.GENDER_POPULARITY_RATIO:
                return 'genderRatioFormatter'
            elif self is ResultsView.DataType.SCORE or self is ResultsView.DataType.GENDER_SCORE_DIFFERENCE:
                return 'scoreFormatter'
            else:
                return 'percentageFormatter'
