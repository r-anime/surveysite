from django.http import HttpRequest, HttpResponse, JsonResponse
from django.forms.models import model_to_dict
from django.views.generic import View
from survey.views.results import ResultsGenerator
from survey.models import Anime, Survey

class IndexApi(View):
    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        year_param = request.GET.get('year', '')
        try:
            year = int(year_param) if year_param else None
        except ValueError:
            return JsonResponse({})
        
        survey_queryset = Survey.objects.filter(year=year) if year else Survey.objects.all()
        survey_dict_list = [model_to_dict(survey, fields=['year', 'season', 'is_preseason']) for survey in survey_queryset]
        
        #results_list = [ResultsGenerator(survey).get_anime_results_data() for survey in survey_queryset]
        return JsonResponse({'surveys': survey_dict_list})
