from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404 # HttpResponse
from django.db.models import F, Q, Avg
from django.db.models.query import EmptyQuerySet
from django.contrib.auth.decorators import login_required, user_passes_test
#from django.template import loader
from datetime import datetime
from enum import Enum, auto
import allauth

from .models import Survey, Anime, AnimeName, Response, AnimeResponse, SurveyAdditionRemoval
from .util import AnimeUtil


# ======= VIEWS =======
# Index
def index(request):
    survey_queryset = Survey.objects.order_by('-year', '-season', 'is_preseason')
    context = {
        'survey_list': survey_queryset,
        'username': get_username(request.user),
    }

    return render(request, 'survey/index.html', context)


def reddit_check(user):
    if not user.is_authenticated: return False

    reddit_accounts = user.socialaccount_set.filter(provider='reddit')
    return len(reddit_accounts) > 0

# Returns None if not authenticated
def get_username(user):
    if not user.is_authenticated: return None

    if len(user.socialaccount_set.all()) > 0:
        return user.socialaccount_set.all()[0].uid
    else:
        return user.username

#@user_passes_test(reddit_check)
@login_required
def form(request, year, season, pre_or_post):
    survey = get_survey_or_404(year, season, pre_or_post)
    _, anime_series_list, special_anime_list = get_survey_anime(survey)

    def modify(anime):
        names = anime.animename_set.all()

        anime.japanese_name = names.filter(anime_name_type=AnimeName.AnimeNameType.JAPANESE_NAME, official=True).first()
        anime.english_name  = names.filter(anime_name_type=AnimeName.AnimeNameType.ENGLISH_NAME , official=True).first()
        anime.short_name    = names.filter(anime_name_type=AnimeName.AnimeNameType.SHORT_NAME   , official=True).first()
        img = anime.image_set.first()
        anime.img = img if img else None

        return anime

    anime_series_list = [modify(anime) for anime in anime_series_list]
    special_anime_list = [modify(anime) for anime in special_anime_list]

    context = {
        'survey': survey,
        'anime_series_list': anime_series_list,
        'special_anime_list': special_anime_list,
        'username': get_username(request.user),
    }
    return render(request, 'survey/form.html', context)

def results(request, year, season, pre_or_post):
    survey = get_survey_or_404(year, season, pre_or_post)
    # Only display results if the survey is not ongoing, or if the user is staff
    if survey.is_ongoing and not request.user.is_staff:
        return redirect('survey:form', survey.year, survey.season, pre_or_post)

    anime_response_queryset = AnimeResponse.objects.filter(response__survey=survey)
    response_count = Response.objects.filter(survey=survey).count()

    _, anime_series_list, special_anime_list = get_survey_anime(survey)
    survey_additions_removals = SurveyAdditionRemoval.objects.filter(survey=survey)


    # +----------------+
    # | GET ANIME DATA |
    # +----------------+
    class DataType(Enum):
        POPULARITY              = "Popularity (%)"
        GENDER_POPULARITY_RATIO = "Gender Ratio (M:F)"
        UNDERWATCHED            = "Underwatched (%)"
        SCORE                   = "Score (x/5)"
        GENDER_SCORE_DIFFERENCE = "Gender Score Difference (M-F)"
        SURPRISE                = "Surprise (%)"
        DISAPPOINTMENT          = "Disappointment (%)"
    
    def get_adjusted_response_count(addition_removal_list, response_count):
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
                addition_count = addition_removal_list[i] if i < len(addition_removal_list) else response_count

                adjusted_response_count -= addition_count - removal_count
                last_count = addition_count
                i += 1

        return adjusted_response_count

    # Returns a dict of data values for an anime
    def get_data_for_anime(anime):
        responses_for_anime = anime_response_queryset.filter(anime=anime)
        responses_by_watchers = responses_for_anime.filter(watching=True)

        # Adjust response count for this anime taking into account the times the anime was added/removed to the survey
        addition_removal_list = list(survey_additions_removals.filter(anime=anime))
        adjusted_response_count = get_adjusted_response_count(addition_removal_list, response_count)

        # Amount of people watching
        watcher_count = responses_by_watchers.count()
        male_response_count = responses_by_watchers.filter(response__gender=Response.Gender.MALE).count()
        female_response_count = responses_by_watchers.filter(response__gender=Response.Gender.FEMALE).count()

        responses_with_score = responses_for_anime.filter(score__isnull=False) if survey.is_preseason else responses_by_watchers.filter(score__isnull=False)
        # Becomes NaN if there are no scores (default behavior is None which causes errors, hence "or NaN" being necessary)
        male_average_score = responses_with_score.filter(response__gender=Response.Gender.MALE).aggregate(Avg('score'))['score__avg'] or float('NaN')
        female_average_score = responses_with_score.filter(response__gender=Response.Gender.FEMALE).aggregate(Avg('score'))['score__avg'] or float('NaN')

        return {
            DataType.POPULARITY:              watcher_count / adjusted_response_count * 100.0 if adjusted_response_count > 0 else float('NaN'),
            DataType.GENDER_POPULARITY_RATIO: male_response_count / female_response_count if female_response_count > 0 else float('inf'),
            DataType.UNDERWATCHED:            responses_with_score.filter(underwatched=True).count() / watcher_count * 100.0 if watcher_count > 0 else float('NaN'),
            DataType.SCORE:                   responses_with_score.aggregate(Avg('score'))['score__avg'] or float('NaN'),
            DataType.GENDER_SCORE_DIFFERENCE: male_average_score - female_average_score if min(male_average_score, female_average_score) > 0 else float('NaN'),
            DataType.SURPRISE:                responses_by_watchers.filter(expectations=AnimeResponse.Expectations.SURPRISE).count() / watcher_count * 100.0 if watcher_count > 0 else float('NaN'),
            DataType.DISAPPOINTMENT:          responses_by_watchers.filter(expectations=AnimeResponse.Expectations.DISAPPOINTMENT).count() / watcher_count * 100.0 if watcher_count > 0 else float('NaN'),
        }

    # Get a dict of data values for each anime (i.e. a dict with for each anime a dict with data values, dict[anime][data])
    anime_series_data = {
        anime: get_data_for_anime(anime) for anime in anime_series_list
    }
    special_anime_data = {
        anime: get_data_for_anime(anime) for anime in special_anime_list
    }


    # +----------------------------+
    # | TABLE GENERATION FUNCTIONS |
    # +----------------------------+
    # Generate table data as a list of rows
    def generate_table_data(anime_data, data_types_to_display):
        table_data = []

        for anime in anime_data.keys():
            row = {"anime": str(anime)}
            for data_type in data_types_to_display:
                row[data_type.name] = anime_data[anime][data_type]
            table_data.append(row)
    
        return table_data
    
    def generate_table(anime_data, table_name, data_types_to_display, data_type_to_sort_by=None, reverse_sort=True):
        if not data_type_to_sort_by:
            data_type_to_sort_by = data_types_to_display[0]
        
        table = {
            'title': table_name,
            'data': None,
            'columns': None,
        }

        table_data = generate_table_data(anime_data, data_types_to_display)
        
        table_data.sort(
            key=lambda row: 0 if row[data_type_to_sort_by.name] == float('inf') or row[data_type_to_sort_by.name] == float('nan') else row[data_type_to_sort_by.name],
            reverse=reverse_sort
        )
        for i in range(len(table_data)):
            table_data[i]['rank'] = i+1
        
        table['data'] = table_data
        table['columns'] = [{
                'key': data_type.name,
                'label': data_type.value,
                'sortable': True,
            } for data_type in data_types_to_display
        ]
        table['columns'] = [{
                'key': 'rank',
                'label': '#',
                'sortable': True,
            }, {
                'key': 'anime',
                'label': 'Anime',
                'sortable': True,
            }
        ] + table['columns']
            
        return table


    # +--------+
    # | TABLES |
    # +--------+
    popularity_table = generate_table(
        anime_series_data,
        'Most Popular Anime',
        [DataType.POPULARITY],
    )
    gender_popularity_ratio_table = generate_table(
        anime_series_data,
        'Biggest Gender Popularity Disparity',
        [DataType.GENDER_POPULARITY_RATIO, DataType.POPULARITY],
    )
    underwatched_table = generate_table(
        anime_series_data,
        'Most Underwatched Anime',
        [DataType.UNDERWATCHED, DataType.POPULARITY],
    )

    score_table = generate_table(
        anime_series_data,
        'Most Anticipated Anime' if survey.is_preseason else 'Best Anime of the Season',
        [DataType.SCORE],
    )
    gender_score_difference_table = generate_table(
        anime_series_data,
        'Biggest Gender Score Disparity',
        [DataType.GENDER_SCORE_DIFFERENCE, DataType.SCORE],
    )

    surprise_table = generate_table(
        anime_series_data,
        'Most Surprising Anime',
        [DataType.SURPRISE, DataType.SCORE],
    )
    disappointment_table = generate_table(
        anime_series_data,
        'Most Disappointing Anime',
        [DataType.DISAPPOINTMENT, DataType.SCORE],
    )
    
    special_popularity_table = generate_table(
        special_anime_data,
        'Most Popular Anime OVAs/ONAs/Movies/Specials',
        [DataType.POPULARITY],
    )
    special_score_table = generate_table(
        special_anime_data,
        'Most Anticipated Anime OVAs/ONAs/Movies/Specials' if survey.is_preseason else 'Best Anime OVAs/ONAs/Movies/Specials',
        [DataType.SCORE],
    )

    table_list = [
        popularity_table, gender_popularity_ratio_table, underwatched_table,
        score_table, gender_score_difference_table,
        surprise_table, disappointment_table,
        special_popularity_table, special_score_table
    ]
    
    context = {
        'survey': survey,
        'table_list': table_list,
        'username': get_username(request.user),
    }
    return render(request, 'survey/results.html', context)

# https://www.reddit.com/wiki/api
# https://django-allauth.readthedocs.io/en/latest/overview.html
# https://tech.serhatteker.com/post/2020-06/custom-signup-view-in-django-allauth/
# https://github.com/pennersr/django-allauth/tree/master/allauth/templates/account

# POST requests will be sent here
#@user_passes_test(reddit_check)
@login_required
def submit(request, year, season, pre_or_post):
    survey = get_survey_or_404(year, season, pre_or_post)
    if request.method == 'POST' and survey.is_ongoing:
        anime_list, _, _ = get_survey_anime(survey)

        response = Response(
            survey=survey,
            timestamp=datetime.now(),
            age=try_get_response(request, 'age', lambda x: int(x), 0),
            gender=try_get_response(request, 'gender', lambda x: Response.Gender(x), ''),
        )
        response.save()

        anime_response_list = []
        for anime in anime_list:
            # Check if the response contains the current anime
            has_anime = False
            for key in request.POST.keys():
                # The key has to both exist in the POST request, and its accompanying value has to be something (in case of score/expectations)
                if key.startswith(str(anime.id)) and request.POST[key]:
                    has_anime = True
                    break
            if not has_anime:
                continue

            anime_response = AnimeResponse(
                response=response,
                anime=anime,
                watching=try_get_response(request, str(anime.id) + '-watched', lambda _: True, False),
                score=try_get_response(request, str(anime.id) + '-score', lambda x: int(x), None),
                underwatched=try_get_response(request, str(anime.id) + '-underwatched', lambda _: True, False),
                expectations=try_get_response(request, str(anime.id) + '-expectations', lambda x: AnimeResponse.Expectations(x), ''),
            )
            anime_response_list.append(anime_response)
        
        AnimeResponse.objects.bulk_create(anime_response_list)
        
        return redirect('survey:index')
    else:
        return redirect('survey:form', survey.year, survey.season, pre_or_post)



# ======= HELPER METHODS =======
def get_survey_anime(survey):
    current_year_season = AnimeUtil.combine_year_season(survey.year, survey.season)

    anime_queryset = AnimeUtil.annotate_year_season(
        Anime.objects
    ).filter(
        AnimeUtil.is_ongoing_filter_func(current_year_season)
    )


    anime_series_filter = AnimeUtil.anime_series_filter
    special_anime_filter = AnimeUtil.special_anime_filter

    # Special anime in pre-season surveys have to start in the survey's season and in post-season surveys have to end in that season,
    # because I cba to track when/whether individual parts of irregularly-released stuff releases
    if survey.is_preseason:
        special_anime_filter = special_anime_filter & Q(start_year_season=current_year_season)
    else:
        special_anime_filter = special_anime_filter & Q(subbed_year_season=current_year_season)
    
    
    anime_series_queryset = anime_queryset.filter(
        anime_series_filter
    )
    special_anime_queryset = anime_queryset.filter(
        special_anime_filter
    )
    combined_anime_queryset = anime_queryset.filter(
        anime_series_filter | special_anime_filter
    )
    return combined_anime_queryset, anime_series_queryset, special_anime_queryset

def get_survey_or_404(year, season, pre_or_post):
    if pre_or_post == 'pre':
        is_preseason = True
    elif pre_or_post == 'post':
        is_preseason = False
    else:
        raise Http404("Survey does not exist!")

    survey = get_object_or_404(Survey, year=year, season=season, is_preseason=is_preseason)
    return survey

def try_get_response(request, item, conversion=None, value_if_none=None):
    if item not in request.POST.keys() or request.POST[item] == '':
        return value_if_none
    else:
        if conversion is None:
            return None
        else:
            return conversion(request.POST[item])
