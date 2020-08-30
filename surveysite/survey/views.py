from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404 # HttpResponse
#from django.template import loader
from .models import Survey, Anime


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
    survey = get_survey_or_404(year, season, pre_or_post)
    return Http404()



# ======= HELPER METHODS =======
def get_survey_anime(survey):
    anime_list = Anime.objects.filter(
        start_year__lte=survey.year,
        start_season__lte=survey.season,
        end_year__gte=survey.year,
        end_season__lte=survey.season,
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