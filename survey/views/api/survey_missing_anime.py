from django.http.request import HttpRequest
from django.http.response import JsonResponse
from django.views.generic import View
from http import HTTPStatus
import json
from survey.models import Survey
from survey.util.http import JsonErrorResponse
from survey.util.survey import get_survey_or_404
from typing import Any

class SurveyMissingAnimeApi(View):
    def post(self, request: HttpRequest, *args, **kwargs):
        survey = get_survey_or_404(
            year=self.kwargs['year'],
            season=self.kwargs['season'],
            pre_or_post=self.kwargs['pre_or_post'],
        )

        if survey.state == Survey.State.UPCOMING:
            return JsonErrorResponse('This survey is not open yet!', HTTPStatus.FORBIDDEN)
        elif survey.state == Survey.State.FINISHED:
            return JsonErrorResponse('This survey has already finished!', HTTPStatus.FORBIDDEN)
            
        json_data: dict[str, dict[str, Any]] = json.loads(request.body)
        print(json_data)

        return JsonResponse({})