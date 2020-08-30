from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404 # HttpResponse
from django.db.models import F
#from django.template import loader
from .models import Survey, Anime, Response, ResponseAnime
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
    context = {
        'survey': survey,
        'anime_list': get_survey_anime(survey),
    }
    return render(request, 'survey/form.html', context)

def results(request, survey):
    context = {
        'survey': survey,
    }
    return render(request, 'survey/results.html', context)



# POST requests will be sent here
def submit(request, year, season, pre_or_post):
    if request.method == 'POST':
        survey = get_survey_or_404(year, season, pre_or_post)
        anime_list = get_survey_anime(survey)

        response = Response(
            survey=survey,
            timestamp=datetime.now(),
            age=try_get_response(request, 'age', lambda x: int(x), 0),
            gender=try_get_response(request, 'gender', lambda x: Response.Gender(x), ''),
        )
        response.save()

        for anime in anime_list:
            if str(anime.id) + '-watched' in request.POST.keys():
                response_anime = ResponseAnime(
                    response=response,
                    anime=anime,
                    score=try_get_response(request, str(anime.id) + '-score', lambda x: int(x), None),
                    underwatched=try_get_response(request, str(anime.id) + '-underwatched', lambda _: True, False),
                    expectations=try_get_response(request, str(anime.id) + '-expectations', lambda x: ResponseAnime.Expectations(x), ''),
                )
                response_anime.save()
        
        return redirect('survey:index')
    else:
        raise Http404()



# ======= HELPER METHODS =======
def get_survey_anime(survey):
    anime_list = Anime.objects.annotate(
        start_year_season = F('start_year') * 10 + F('start_season'),
        end_year_season   = F('end_year')   * 10 + F('end_season'),
    )
    anime_list = anime_list.filter(
        start_year_season__lte=survey.year*10+survey.season,
        end_year_season__gte=survey.year*10+survey.season,
    )
    return anime_list

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
