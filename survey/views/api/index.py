from django.core.serializers import serialize
from django.http import HttpRequest, HttpResponse
from django.views.generic import View
from survey.models import Survey
from survey.views.api import JsonResponse

class IndexApi(View):
    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        year_param = request.GET.get('year', '')
        try:
            year = int(year_param) if year_param else None
        except ValueError:
            return JsonResponse([])
        
        survey_queryset = Survey.objects.filter(year=year) if year else Survey.objects.all()
        return JsonResponse(survey_queryset)
