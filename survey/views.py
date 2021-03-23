from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404 # HttpResponse
from django.db.models import F, Q, Avg
from django.db.models.query import EmptyQuerySet
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.cache import cache
#from django.template import loader
from datetime import datetime
from enum import Enum, auto
import allauth
import logging

from .models import Survey, Anime, AnimeName, Response, AnimeResponse, SurveyAdditionRemoval
from .util import AnimeUtil, SurveyUtil, get_user_info
from .resultview import ResultsGenerator, ResultsType


# ======= VIEWS =======
def index(request):
    """Generates the index view, containing a list of current and past surveys."""
    survey_queryset = Survey.objects.order_by('-year', '-season', 'is_preseason')


    for survey in survey_queryset:
        if survey.is_ongoing:
            score_ranking = []
        else:
            def get_score_ranking():
                anime_series_results, _ = ResultsGenerator(survey).get_anime_results_data()
                return sorted(
                    [(anime, anime_data[ResultsType.SCORE]) for anime, anime_data in anime_series_results.items()],
                    key=lambda item: item[1] if item[1] == item[1] else -1,
                    reverse=True,
                )

            if SurveyUtil.is_survey_old(survey):
                score_ranking = cache.get_or_set('survey_score_ranking_%i' % survey.id, get_score_ranking, version=1, timeout=SurveyUtil.get_old_survey_cache_timeout())
            else:
                score_ranking = get_score_ranking()

        
        survey.score_ranking = score_ranking[:3]

    context = {
        'survey_list': survey_queryset,
        'user_info': get_user_info(request.user),
    }

    return render(request, 'survey/index.html', context)


#@user_passes_test(__reddit_check)
@login_required
def form(request, year, season, pre_or_post):
    """Generates the form view, where users can respond to a survey. Requires the user being logged in."""
    survey = SurveyUtil.get_survey_or_404(year, season, pre_or_post)

    if __session_is_survey_answered(request, survey):
        messages.info(request, 'You already filled in %s!' % str(survey))
        return redirect('survey:index')


    _, anime_series_list, special_anime_list = SurveyUtil.get_survey_anime(survey)

    def modify(anime):
        names = anime.animename_set.all()

        japanese_name = names.filter(anime_name_type=AnimeName.AnimeNameType.JAPANESE_NAME, official=True).first()
        anime.japanese_name = japanese_name if japanese_name else names.filter(anime_name_type=AnimeName.AnimeNameType.JAPANESE_NAME, official=False).first()
        english_name  = names.filter(anime_name_type=AnimeName.AnimeNameType.ENGLISH_NAME , official=True).first()
        anime.english_name  = english_name  if english_name  else names.filter(anime_name_type=AnimeName.AnimeNameType.ENGLISH_NAME , official=False).first()
        short_name    = names.filter(anime_name_type=AnimeName.AnimeNameType.SHORT_NAME   , official=True).first()
        anime.short_name    = short_name    if short_name    else names.filter(anime_name_type=AnimeName.AnimeNameType.SHORT_NAME   , official=False).first()

        return anime

    anime_series_list = [modify(anime) for anime in anime_series_list]
    special_anime_list = [modify(anime) for anime in special_anime_list]

    context = {
        'survey': survey,
        'anime_series_list': anime_series_list,
        'special_anime_list': special_anime_list,
        'user_info': get_user_info(request.user),
    }
    return render(request, 'survey/form.html', context)


#@user_passes_test(__reddit_check)
@login_required
def submit(request, year, season, pre_or_post):
    """A view saving a user's response to a survey to a database, and redirecting them back to the index. Requires the user being logged in."""
    survey = SurveyUtil.get_survey_or_404(year, season, pre_or_post)

    if __session_is_survey_answered(request, survey):
        messages.info(request, 'You already filled in %s!' % str(survey))
        return redirect('survey:index')


    if request.method == 'POST' and survey.is_ongoing:
        anime_list, _, _ = SurveyUtil.get_survey_anime(survey)

        try:
            response = Response(
                survey=survey,
                timestamp=datetime.now(),
                age=__try_get_response(request, 'age', lambda x: int(x)),
                gender=__try_get_response(request, 'gender', lambda x: Response.Gender(x)),
            )
            response.clean_fields()
        except (ValueError, ValidationError) as e:
            messages.error(request, 'Submitted an invalid age or gender not one of the possible options')
            logging.warning('User sent one or more invalid values:\n  %s: "%s"\n  %s: "%s"' % ('age', request.POST.get('age', None), 'gender', request.POST.get('gender', None)))
            return redirect('survey:form', survey.year, survey.season, pre_or_post)
        except Exception as e:
            messages.error(request, 'Something went wrong during response submission')
            logging.error('Unknown exception occurred during response validation:\nPOST values:\n%s\n\nException:\n%s' % (str(request.POST), str(e)))
            return redirect('survey:form', survey.year, survey.season, pre_or_post)
        else:
            response.save()


        anime_response_list = []
        for anime in anime_list:
            # Check if the response contains the current anime
            has_anime = False
            for key in request.POST.keys():
                # The key has to both exist in the POST request, and its accompanying value has to be something (in case of score/expectations)
                if key.startswith(str(anime.id)) and request.POST.get(key, None):
                    has_anime = True
                    break
            if not has_anime:
                continue

            anime_str = ' / '.join(AnimeUtil.get_name_list(anime))
            try:
                anime_response = AnimeResponse(
                    response=response,
                    anime=anime,
                    watching=__try_get_response(request, str(anime.id) + '-watched', lambda _: True, False),
                    score=__try_get_response(request, str(anime.id) + '-score', lambda x: int(x), None),
                    underwatched=__try_get_response(request, str(anime.id) + '-underwatched', lambda _: True, False),
                    expectations=__try_get_response(request, str(anime.id) + '-expectations', lambda x: AnimeResponse.Expectations(x), ''),
                )
                anime_response.clean_fields()
            except (ValueError, ValidationError) as e:
                messages.error(request, 'Submitted invalid score or expectation for anime "%s"' % anime_str)
                logging.warning('User sent one or more invalid values for anime "%i":\n  %s: "%s"\n  %s: "%s"' % (anime.id, 'score', request.POST.get(str(anime.id) + '-score', None), 'expectations', request.POST.get(str(anime.id) + '-expectations', None)))
                response.delete()
                return redirect('survey:form', survey.year, survey.season, pre_or_post)
            except Exception as e:
                messages.error(request, 'Something went wrong during submitting your response for anime "%s"' % anime_str)
                logging.error('Unknown exception occurred during response validation for anime %i:\nPOST values:\n%s\n\nException:\n%s' % (anime.id, str(request.POST), str(e)))
                return redirect('survey:form', survey.year, survey.season, pre_or_post)
            else:
                anime_response_list.append(anime_response)
        
        AnimeResponse.objects.bulk_create(anime_response_list)
        
        __session_set_survey_answered(request, survey)
        messages.success(request, "Successfully filled in %s!" % str(survey))
        return redirect('survey:index')
    else:
        return redirect('survey:form', survey.year, survey.season, pre_or_post)



# ======= HELPER METHODS =======
def __try_get_response(request, item, conversion, value_if_none=None):
    """Tries to get the specified value of an item from the POST request.

    Parameters
    ----------
    request : HttpRequest
        The request sent by the user. Must be a POST request.
    item : str
        The item (key) you want to get the value of.
    conversion : lambda
        Converts the item's value (if it exists).
    value_if_none : any, optional
        Value that gets returned if the item or value doesn't exist or is empty, by default None.

    Returns
    -------
    any
        The value of the item.
    """

    if item not in request.POST.keys() or request.POST.get(item, '') == '':
        return value_if_none
    else:
        return conversion(request.POST.get(item, None))

# Forgot why I stopped using this
def __reddit_check(user):
    """Returns True if the user is authenticated via Reddit."""
    if not user.is_authenticated: return False

    reddit_accounts = user.socialaccount_set.filter(provider='reddit')
    return len(reddit_accounts) > 0

def __session_set_survey_answered(request, survey):
    """Store that the given survey is answered in the session data."""
    key = 'answered_survey_%i' % survey.id
    request.session[key] = True

def __session_is_survey_answered(request, survey):
    """Check whether the user answered a certain survey."""
    key = 'answered_survey_%i' % survey.id
    return key in request.session
