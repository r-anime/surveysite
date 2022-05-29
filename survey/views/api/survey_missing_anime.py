from dataclasses import dataclass
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.http.request import HttpRequest
from django.http.response import JsonResponse
from django.utils.decorators import method_decorator
from django.views.generic import View
from http import HTTPStatus
import json
import logging
from survey.models import MissingAnime, Survey
from survey.util.data import DataBase
from survey.util.http import HttpEmptyErrorResponse, JsonErrorResponse
from survey.util.survey import try_get_survey
from typing import Any, Optional

@method_decorator(login_required, name='put')
class SurveyMissingAnimeApi(View):
    def put(self, request: HttpRequest, *args, **kwargs):
        survey = try_get_survey(
            year=self.kwargs['year'],
            season=self.kwargs['season'],
            pre_or_post=self.kwargs['pre_or_post'],
        )
        if survey is None:
            return HttpEmptyErrorResponse(HTTPStatus.NOT_FOUND)

        if survey.state == Survey.State.UPCOMING:
            return JsonErrorResponse('This survey is not open yet!', HTTPStatus.FORBIDDEN)
        elif survey.state == Survey.State.FINISHED:
            return JsonErrorResponse('This survey has already finished!', HTTPStatus.FORBIDDEN)
            
        json_data: dict[str, dict[str, Any]] = json.loads(request.body)

        try:
            missing_anime_data = MissingAnimeData.from_dict(json_data)
        except KeyError as e:
            logging.error('An error occurred while parsing missing anime data: ' + str(e))
            return JsonErrorResponse('Request data is invalid', HTTPStatus.BAD_REQUEST)

        validation_errors = {}

        missing_anime = missing_anime_data.to_model()
        try:
            missing_anime.full_clean()
        except ValidationError as e:
            logging.warning('A validation error occurred while a user was submitting missing aniem to survey "%s":\r\n%s', str(survey), str(e.message_dict))
            validation_errors['missing_anime'] = e.message_dict

        if validation_errors:
            return JsonErrorResponse({'validation': validation_errors}, HTTPStatus.BAD_REQUEST)

        missing_anime.survey = survey
        missing_anime.user = request.user
        missing_anime.save()

        return JsonResponse({}, status=HTTPStatus.NO_CONTENT)

@dataclass
class MissingAnimeData(DataBase):
    name: str
    link: str
    description: str

    def to_model(self, model: Optional[MissingAnime]=None):
        if model is None:
            return MissingAnime(
                name=self.name,
                link=self.link,
                description=self.description,
            )
        else:
            model.name = self.name
            model.link = self.link
            model.description = self.description
            return model
