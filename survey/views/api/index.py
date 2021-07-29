from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.generic import View
from survey.models import Survey
from survey.util import json_encoder_factory
from survey.views.results import ResultsGenerator

class IndexApi(View):
    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        year_param = request.GET.get('year', '')
        try:
            year = int(year_param) if year_param else None
        except ValueError:
            return JsonResponse({})
        
        survey_list = list(Survey.objects.filter(year=year) if year else Survey.objects.all())
        jsonEncoder = json_encoder_factory(fields_per_model={ Survey: ['year', 'season', 'is_preseason'] })
        
        #results_list = [ResultsGenerator(survey).get_anime_results_data() for survey in survey_queryset]
        return JsonResponse({'surveys': survey_list}, encoder=jsonEncoder)
