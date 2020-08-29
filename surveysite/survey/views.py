from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404 # HttpResponse
#from django.template import loader
from .models import Survey

def index(request):
    survey_list = Survey.objects.order_by('year_season', 'is_preseason')
    context = {
        'survey_list': survey_list,
    }

    return render(request, 'survey/index.html', context)

def survey(request, year_season, pre_or_post):
    survey = get_survey_or_404(year_season, pre_or_post)
    if survey.is_ongoing:
        return form(request, survey)
    else:
        return results(request, survey)

def form(request, survey):
    context = {
        'survey': survey,
    }
    return render(request, 'survey/form.html', context)

def results(request, survey):
    context = {
        'survey': survey,
    }
    return render(request, 'survey/results.html', context)

def submit(request, year_season, pre_or_post):
    survey = get_survey_or_404(year_season, pre_or_post)
    return Http404()

def get_survey_or_404(year_season, pre_or_post):
    if pre_or_post == 'pre':
        is_preseason = True
    elif pre_or_post == 'post':
        is_preseason = False
    else:
        raise Http404("Survey does not exist!")

    survey = get_object_or_404(Survey, year_season=year_season, is_preseason=is_preseason)
    return survey