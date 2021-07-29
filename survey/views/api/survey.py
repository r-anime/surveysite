from django.http import JsonResponse
from django.views.generic import View

class SurveyApi(View):
    def get(self, request, *args, **kwargs):
        return JsonResponse()
