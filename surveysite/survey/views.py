from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404 # HttpResponse
from django.db.models import F, Q, Avg
from django.db.models.query import EmptyQuerySet
#from django.template import loader
from datetime import datetime
from enum import Enum, auto

from .models import Survey, Anime, AnimeName, Response, AnimeResponse
from .util import AnimeUtil


# ======= VIEWS =======
# Index
def index(request):
    survey_queryset = Survey.objects.order_by('year', 'season', 'is_preseason')
    context = {
        'survey_list': survey_queryset,
    }

    return render(request, 'survey/index.html', context)


# Survey page, use form() if survey active, otherwise use results()
def survey(request, year, season, pre_or_post):
    survey = get_survey_or_404(year, season, pre_or_post)
    if survey.is_ongoing:
        return form(request, survey)
    else:
        return results(request, survey)

def form(request, survey):
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
    }
    return render(request, 'survey/form.html', context)

def results(request, survey):
    anime_response_queryset = AnimeResponse.objects.filter(response__survey=survey)
    response_count = Response.objects.filter(survey=survey).count()

    anime_list, anime_series_list, special_anime_list = get_survey_anime(survey)


    # +----------------+
    # | GET ANIME DATA |
    # +----------------+
    class DataType(Enum):
        POPULARITY              = auto()
        GENDER_POPULARITY_RATIO = auto()
        UNDERWATCHED            = auto()
        SCORE                   = auto()
        GENDER_SCORE_DIFFERENCE = auto()
        SURPRISE                = auto()
        DISAPPOINTMENT          = auto()
    
    # Returns a dict of data values for an anime
    def get_data_for_anime(anime):
        if survey.is_preseason:
            responses_for_anime = anime_response_queryset.filter(anime=anime)
        else:
            responses_for_anime = anime_response_queryset.filter(anime=anime, watching=True)

        male_response_count = responses_for_anime.filter(response__gender=Response.Gender.MALE).count()
        female_response_count = responses_for_anime.filter(response__gender=Response.Gender.FEMALE).count()

        responses_with_score = responses_for_anime.filter(score__isnull=False)
        # Becomes NaN if there are no scores (default behavior is None which causes errors, hence "or NaN" being necessary)
        male_average_score = responses_with_score.filter(response__gender=Response.Gender.MALE).aggregate(Avg('score'))['score__avg'] or float('NaN')
        female_average_score = responses_with_score.filter(response__gender=Response.Gender.FEMALE).aggregate(Avg('score'))['score__avg'] or float('NaN')

        watchers_count = responses_for_anime.filter(watching=True).count()

        return {
            DataType.POPULARITY:              watchers_count / response_count * 100.0 if response_count > 0 else float('NaN'),
            DataType.GENDER_POPULARITY_RATIO: male_response_count / female_response_count if female_response_count > 0 else float('inf'),
            DataType.UNDERWATCHED:            responses_with_score.filter(underwatched=True).count() / watchers_count * 100.0 if watchers_count > 0 else float('NaN'),
            DataType.SCORE:                   responses_with_score.aggregate(Avg('score'))['score__avg'] or float('NaN'),
            DataType.GENDER_SCORE_DIFFERENCE: male_average_score - female_average_score if min(male_average_score, female_average_score) > 0 else float('NaN'),
            DataType.SURPRISE:                responses_for_anime.filter(expectations=AnimeResponse.Expectations.SURPRISE).count() / watchers_count * 100.0 if watchers_count > 0 else float('NaN'),
            DataType.DISAPPOINTMENT:          responses_for_anime.filter(expectations=AnimeResponse.Expectations.DISAPPOINTMENT).count() / watchers_count * 100.0 if watchers_count > 0 else float('NaN'),
        }

    # Get a dict of data values for each anime (i.e. a dict with for each anime a dict with data values, dict[anime][data])
    anime_series_data = {
        anime: get_data_for_anime(anime) for anime in anime_series_list
    }
    special_anime_data = {
        anime: get_data_for_anime(anime) for anime in special_anime_list
    }


    # +-----------------+
    # | GENERATE TABLES |
    # +-----------------+
    # Generate table data as a list of rows
    def generate_table_data(anime_data, column_name_list, sorting_column=0, descending=True):
        table_data = []

        for anime in anime_data.keys():
            row = [str(anime)]

            for column_name in column_name_list:
                row.append(anime_data[anime][column_name])
            
            table_data.append(row)
        
        table_data.sort(
            key=lambda row: 0 if row[1+sorting_column] == float('inf') else row[1+sorting_column],
            reverse=descending
        )
        for i in range(len(table_data)):
            table_data[i].insert(0, i+1)
        
        return table_data

    popularity_table = {
        'title': 'Most Popular Anime',
        'headers': ['#', 'Anime', '%'],
        'data': generate_table_data(anime_series_data, [DataType.POPULARITY])[:10]
    }
    gender_popularity_ratio_data = generate_table_data(anime_series_data, [DataType.GENDER_POPULARITY_RATIO, DataType.POPULARITY])
    gender_popularity_ratio_table = {
        'title': 'Biggest Gender Popularity Disparity',
        'headers': ['#', 'Anime', 'M:F Ratio', 'Popularity'],
        'data': gender_popularity_ratio_data[:3] + [['', '...', '...', '...']] + gender_popularity_ratio_data[-3:]
    }
    underwatched_table = {
        'title': 'Most Underwatched Anime',
        'headers': ['#', 'Anime', '%', 'Popularity'],
        'data': generate_table_data(anime_series_data, [DataType.UNDERWATCHED, DataType.POPULARITY])[:5]
    }

    score_data = generate_table_data(anime_series_data, [DataType.SCORE])
    score_table = {
        'title': 'Most Anticipated Anime' if survey.is_preseason else 'Best/Worst Anime',
        'headers': ['#', 'Anime', 'Score'],
        'data': score_data[:10] + [['', '...', '...']] + score_data[-5:]
    }
    gender_score_difference_data = generate_table_data(anime_series_data, [DataType.GENDER_SCORE_DIFFERENCE, DataType.SCORE])
    gender_score_difference_table = {
        'title': 'Biggest Gender Score Disparity',
        'headers': ['#', 'Anime', 'M-F Score', 'Score'],
        'data': gender_score_difference_data[:3] + [['', '...', '...', '...']] + gender_score_difference_data[-3:]
    }

    surprise_table = {
        'title': 'Most Surprising Anime',
        'headers': ['#', 'Anime', '%', 'Score'],
        'data': generate_table_data(anime_series_data, [DataType.SURPRISE, DataType.SCORE])[:5]
    }
    disappointment_table = {
        'title': 'Most Disappointing Anime',
        'headers': ['#', 'Anime', '%', 'Score'],
        'data': generate_table_data(anime_series_data, [DataType.DISAPPOINTMENT, DataType.SCORE])[:5]
    }
    
    special_popularity_table = {
        'title': 'Most Popular Anime OVAs/ONAs/Movies/Specials',
        'headers': ['#', 'Anime', '%'],
        'data': generate_table_data(special_anime_data, [DataType.POPULARITY])[:5]
    }
    special_score_table = {
        'title': 'Most Anticipated Anime OVAs/ONAs/Movies/Specials' if survey.is_preseason else 'Best Anime OVAs/ONAs/Movies/Specials',
        'headers': ['#', 'Anime', 'Score'],
        'data': generate_table_data(special_anime_data, [DataType.SCORE])[:5]
    }

    table_list = [
        popularity_table, gender_popularity_ratio_table, underwatched_table,
        score_table, gender_score_difference_table,
        surprise_table, disappointment_table,
        special_popularity_table, special_score_table]
    context = {
        'survey': survey,
        'table_list': table_list,
    }
    return render(request, 'survey/results.html', context)



# POST requests will be sent here
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
        raise Http404()



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
