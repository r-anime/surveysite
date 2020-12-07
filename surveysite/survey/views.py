from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404 # HttpResponse
from django.db.models import F, Q, Avg
from django.db.models.query import EmptyQuerySet
#from django.template import loader
from .models import Survey, Anime, AnimeName, Response, AnimeResponse
from datetime import datetime


# ======= VIEWS =======
# Index
def index(request):
    survey_list = Survey.objects.order_by('year', 'season', 'is_preseason')
    context = {
        'survey_list': survey_list,
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

        return anime

    anime_series_list = [modify(anime) for anime in anime_series_list]

    context = {
        'survey': survey,
        'anime_series_list': anime_series_list,
        'special_anime_list': special_anime_list,
    }
    return render(request, 'survey/form.html', context)

def results(request, survey):
    anime_response_list = AnimeResponse.objects.filter(response__survey=survey)
    response_list = Response.objects.filter(survey=survey)
    response_count = max(response_list.count(), 1)

    _, anime_series_list, special_anime_list = get_survey_anime(survey)

    anime_response_list_per_anime = {
        anime: (anime_response_list.filter(anime=anime) if survey.is_preseason else anime_response_list.filter(anime=anime, watching=True)) for anime in anime_series_list
    }

    # Returns a dict of data values for an anime
    def get_data_for_anime(anime):
        responses_for_anime = anime_response_list_per_anime[anime]
        male_response_count = responses_for_anime.filter(response__gender=Response.Gender.MALE).count()
        female_response_count = responses_for_anime.filter(response__gender=Response.Gender.FEMALE).count()

        return {
            'popularity': responses_for_anime.filter(watching=True).count() / response_count * 100.0,
            'score': responses_for_anime.filter(score__isnull=False).aggregate(Avg('score'))['score__avg'] or 0, # returns 0 if score is None (no scores)
            'gender_popularity_ratio': male_response_count / female_response_count if female_response_count > 0 else float('inf'),
        }

    # Get a dict of data values for each anime (i.e. a dict with for each anime a dict with data values, dict[anime][data])
    data = {
        anime: get_data_for_anime(anime) for anime in anime_response_list_per_anime.keys()
    }

    # Generate table data as a list of rows
    def generate_table_data(column_name_list, sorting_column=0, descending=True):
        table_data = []

        for anime in data.keys():
            row = [str(anime)]

            for column_name in column_name_list:
                row.append(data[anime][column_name])
            
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
        'data': generate_table_data(['popularity'])
    }
    gender_popularity_ratio_table = {
        'title': 'Biggest Gender Popularity Disparity',
        'headers': ['#', 'Anime', 'M:F Ratio'],
        'data': generate_table_data(['gender_popularity_ratio'])
    }
    score_table = {
        'title': 'Most Anticipated Anime' if survey.is_preseason else 'Best Anime',
        'headers': ['#', 'Anime', 'Score'],
        'data': generate_table_data(['score'])
    }

    table_list = [popularity_table, gender_popularity_ratio_table, score_table]
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
            if survey.is_ongoing and str(anime.id) + '-watched' not in request.POST.keys():
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
    current_year_season = survey.year * 10 + survey.season
    year_season_filter = Q(start_year_season__lte=current_year_season) & \
        (Q(end_year_season__gte=current_year_season) | Q(end_year_season=None))

    anime_list = Anime.objects.annotate(
        start_year_season  = F('start_year')  * 10 + F('start_season') ,
        end_year_season    = F('end_year')    * 10 + F('end_season')   ,
        subbed_year_season = F('subbed_year') * 10 + F('subbed_season'),
    ).filter(
        year_season_filter
    )

    anime_series_filter = Q(anime_type=Anime.AnimeType.TV_SERIES) | Q(anime_type=Anime.AnimeType.ONA_SERIES) | Q(anime_type=Anime.AnimeType.BULK_RELEASE)
    special_anime_filter = ~anime_series_filter & Q(subbed_year_season=current_year_season)
    
    anime_series_list = anime_list.filter(
        anime_series_filter
    )
    special_anime_list = anime_list.filter(
        special_anime_filter
    )
    combined_anime_list = anime_list.filter(
        anime_series_filter | special_anime_filter
    )
    return combined_anime_list, anime_series_list, special_anime_list

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
