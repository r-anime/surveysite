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
from .util import AnimeUtil, SurveyUtil, get_username
from .resultview import ResultsGenerator, ResultsType


# ======= VIEWS =======
def index(request):
    """Generates the index view, containing a list of current and past surveys."""
    survey_queryset = Survey.objects.order_by('-year', '-season', 'is_preseason')

    for survey in survey_queryset:
        anime_series_results, _ = ResultsGenerator(survey).get_anime_results_data()
        score_ranking = sorted(
            [(anime, anime_data[ResultsType.SCORE]) for anime, anime_data in anime_series_results.items()],
            key=lambda item: item[1],
            reverse=True,
        )
        
        survey.score_ranking = score_ranking

    context = {
        'survey_list': survey_queryset,
        'username': get_username(request.user),
    }

    return render(request, 'survey/index.html', context)


#@user_passes_test(__reddit_check)
@login_required
def form(request, year, season, pre_or_post):
    """Generates the form view, where users can respond to a survey. Requires the user being logged in."""
    survey = SurveyUtil.get_survey_or_404(year, season, pre_or_post)
    _, anime_series_list, special_anime_list = SurveyUtil.get_survey_anime(survey)

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


#@user_passes_test(__reddit_check)
@login_required
def submit(request, year, season, pre_or_post):
    """A view saving a user's response to a survey to a database, and redirecting them back to the index. Requires the user being logged in."""
    survey = SurveyUtil.get_survey_or_404(year, season, pre_or_post)

    if request.method == 'POST' and survey.is_ongoing:
        anime_list, _, _ = SurveyUtil.get_survey_anime(survey)

        response = Response(
            survey=survey,
            timestamp=datetime.now(),
            age=__try_get_response(request, 'age', lambda x: int(x), 0),
            gender=__try_get_response(request, 'gender', lambda x: Response.Gender(x), ''),
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
                watching=__try_get_response(request, str(anime.id) + '-watched', lambda _: True, False),
                score=__try_get_response(request, str(anime.id) + '-score', lambda x: int(x), None),
                underwatched=__try_get_response(request, str(anime.id) + '-underwatched', lambda _: True, False),
                expectations=__try_get_response(request, str(anime.id) + '-expectations', lambda x: AnimeResponse.Expectations(x), ''),
            )
            anime_response_list.append(anime_response)
        
        AnimeResponse.objects.bulk_create(anime_response_list)
        
        messages.success(request, "Successfully filled in %s!" % str(survey))
        return redirect('survey:index')
    else:
        return redirect('survey:form', survey.year, survey.season, pre_or_post)



# ======= HELPER METHODS =======
def __try_get_response(request, item, conversion=None, value_if_none=None):
    """Tries to get the specified value of an item from the POST request.

    Parameters
    ----------
    request : HttpRequest
        The request sent by the user. Must be a POST request.
    item : str
        The item (key) you want to get the value of.
    conversion : lambda, optional
        Converts the item's value (if it exists), by default None (no conversion).
    value_if_none : any, optional
        Value that gets returned if the item or value doesn't exist or is empty, by default None.

    Returns
    -------
    any
        The value of the item.
    """

    if item not in request.POST.keys() or request.POST[item] == '':
        return value_if_none
    else:
        if conversion is None:
            return None
        else:
            return conversion(request.POST[item])

# Forgot why I stopped using this
def __reddit_check(user):
    """Returns True if the user is authenticated via Reddit."""
    if not user.is_authenticated: return False

    reddit_accounts = user.socialaccount_set.filter(provider='reddit')
    return len(reddit_accounts) > 0
