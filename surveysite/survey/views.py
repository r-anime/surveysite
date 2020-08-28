from django.shortcuts import render, get_object_or_404
from django.http import Http404 # HttpResponse
#from django.template import loader
from .models import Survey

def index(request):
    survey_list = Survey.objects.order_by('year_season', 'is_preseason')
    context = {
        'survey_list': survey_list,
    }

    return render(request, 'survey/index.html', context)

def form(request, year_season, pre_or_post):
    if pre_or_post == 'pre':
        is_preseason = True
    elif pre_or_post == 'post':
        is_preseason = False
    else:
        raise Http404("Survey does not exist!")

    survey = get_object_or_404(Survey, year_season=year_season, is_preseason=is_preseason)
    context = {
        'survey': survey,
    }

    return render(request, 'survey/form.html', context)

def results(request, year_season, pre_or_post):
    if pre_or_post == 'pre':
        is_preseason = True
    elif pre_or_post == 'post':
        is_preseason = False
    else:
        raise Http404("Survey does not exist!")

    survey = get_object_or_404(Survey, year_season=year_season, is_preseason=is_preseason)
    context = {
        'survey': survey,
    }

    return render(request, 'survey/results.html', context)