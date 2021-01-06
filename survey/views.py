from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404 # HttpResponse
from django.db.models import F, Q, Avg
from django.db.models.query import EmptyQuerySet
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
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

    for survey in survey_queryset:
        survey_response_queryset = Response.objects.filter(survey=survey)
        animeresponse_queryset = AnimeResponse.objects.filter(response__in=survey_response_queryset, score__isnull=False)

        score_ranking = []
        for anime in get_survey_anime(survey)[0]:
            anime_score = animeresponse_queryset.filter(anime=anime).aggregate(Avg('score'))['score__avg'] or -1
            score_ranking.append((anime, anime_score))
        
        score_ranking.sort(key=lambda item: item[1], reverse=True)
        
        survey.score_ranking = score_ranking

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
        
        messages.success(request, "Successfully filled in %s!" % str(survey))
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
