from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.http.request import HttpRequest
from django.utils.decorators import method_decorator
from django.utils.functional import classproperty
from django.views.decorators.cache import never_cache
from django.views.generic import View
from hashlib import sha512
from http import HTTPStatus
import json
import logging
from survey.models import AnimeResponse, MtmUserResponse, Response, Survey
from survey.util.anime import anime_is_continuing
from survey.util.data import AnimeData, SurveyData, json_encoder_factory, DataBase
from survey.util.http import HttpEmptyErrorResponse, JsonErrorResponse
from survey.util.survey import try_get_survey, get_survey_anime
from typing import Any, Callable, Optional


# TODO: In the future unauthenticated users should still be able to see the survey
#       but not be able to respond to the survey
@method_decorator(never_cache, name='dispatch')
class SurveyFormApi(View):
    def get(self, request: HttpRequest, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonErrorResponse('You need to be logged in to fill in a survey!', HTTPStatus.UNAUTHORIZED)

        jsonEncoder = json_encoder_factory()

        survey = try_get_survey(
            year=self.kwargs['year'],
            season=self.kwargs['season'],
            pre_or_post=self.kwargs['pre_or_post'],
        )
        if survey is None:
            return JsonErrorResponse('Survey not found!', HTTPStatus.NOT_FOUND)

        if not request.user.is_staff:
            if survey.state == Survey.State.UPCOMING:
                return JsonErrorResponse('This survey is not open yet!', HTTPStatus.FORBIDDEN)
            elif survey.state == Survey.State.FINISHED:
                return JsonErrorResponse('This survey has already finished!', HTTPStatus.FORBIDDEN)

        previous_response, response_was_linked, has_user_responded = try_get_previous_response(request.user, request.GET.get('responseId'), survey)
        if has_user_responded and previous_response is None:
            return JsonErrorResponse('You already responded to this survey!', HTTPStatus.FORBIDDEN)

        anime_list, _, _ = get_survey_anime(survey)

        response_data = ResponseData.from_model(previous_response) if previous_response else ResponseData()
        anime_response_data_dict: dict[int, AnimeResponseData] = {}
        for anime in anime_list:
            previous_animeresponse_queryset = AnimeResponse.objects.filter(response=previous_response, anime=anime)
            if previous_animeresponse_queryset and previous_animeresponse_queryset.count() == 1:
                anime_response_data_dict[anime.id] = AnimeResponseData.from_model(previous_animeresponse_queryset.first())
            else:
                anime_response_data_dict[anime.id] = AnimeResponseData()
        
        response = SurveyFormData(
            survey=SurveyData.from_model(survey),
            response_data=response_data,
            anime_data_dict={anime.id: AnimeData.from_model(anime) for anime in anime_list},
            anime_response_data_dict=anime_response_data_dict,
            is_anime_new_dict={anime.id: not anime_is_continuing(anime, survey) for anime in anime_list},
            is_response_linked_to_user=response_was_linked,
        )

        return JsonResponse(response, encoder=jsonEncoder, safe=False)

    def put(self, request: HttpRequest, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonErrorResponse('You need to be logged in to fill in a survey!', HTTPStatus.UNAUTHORIZED)

        survey = try_get_survey(
            year=self.kwargs['year'],
            season=self.kwargs['season'],
            pre_or_post=self.kwargs['pre_or_post'],
        )
        if survey is None:
            return HttpEmptyErrorResponse(HTTPStatus.NOT_FOUND)

        if survey.state == Survey.State.UPCOMING:
            return JsonErrorResponse('This survey is not open yet!', HTTPStatus.FORBIDDEN)
        elif survey.state == Survey.State.FINISHED and (survey.closing_time - datetime.now()).total_seconds() < 15 * 60:
            # Users can still submit responses 15 minutes after the survey has closed
            return JsonErrorResponse('This survey has already finished!', HTTPStatus.FORBIDDEN)
        
        previous_response, _, has_user_responded = try_get_previous_response(request.user, request.GET.get('responseId'), survey)
        if has_user_responded and previous_response is None:
            return JsonErrorResponse('You already responded to this survey!', HTTPStatus.FORBIDDEN)


        json_data: dict[str, dict[str, Any]] = json.loads(request.body)
        try:
            submit_data = SurveyFromSubmitData.from_dict(json_data)
        except KeyError as e:
            logging.error('An error occurred while parsing form submission data: ' + str(e))
            return JsonErrorResponse('Request data is invalid', HTTPStatus.BAD_REQUEST)

        response_data = submit_data.response_data
        anime_response_data_dict = submit_data.anime_response_data_dict
        link_response_to_user = submit_data.is_response_linked_to_user

        # Remove responses for anime that are not in the survey (anymore)
        survey_anime_queryset, _, _ = get_survey_anime(survey)
        survey_anime_id_set: set[int] = set(survey_anime_queryset.values_list('id', flat=True))
        anime_ids_in_anime_response_data_dict = list(anime_response_data_dict.keys()) # Copy this since we edit the dict
        for anime_id in anime_ids_in_anime_response_data_dict:
            if anime_id not in survey_anime_id_set:
                anime_response_data_dict.pop(anime_id)

        validation_errors = {}

        response = response_data.to_model(previous_response)
        try:
            response.full_clean()
        except ValidationError as e:
            logging.warning('A validation error occurred while a user was submitting a response to survey "%s":\r\n%s', str(survey), str(e.message_dict))
            validation_errors['response_data'] = e.message_dict

        if previous_response is None:
            response.survey = survey

        #########################
        # Actual updating/inserting/deleting of AnimeResponse models
        #########################

        existing_anime_response_queryset = AnimeResponse.objects.filter(response=previous_response)

        anime_responses_to_update: dict[int, AnimeResponse] = { anime_response.anime_id: anime_response for anime_response in existing_anime_response_queryset.filter(anime_id__in=anime_response_data_dict.keys()) } if previous_response else {}
        anime_responses_to_add: list[AnimeResponse] = []
        for anime_id, anime_response_data in anime_response_data_dict.items():
            previous_anime_response = anime_responses_to_update.get(anime_id, None)

            anime_response = anime_response_data.to_model(previous_anime_response)
            try:
                anime_response.full_clean()
            except ValidationError as e:
                if 'anime_response_data_dict' not in validation_errors:
                    validation_errors['anime_response_data_dict'] = {}
                validation_errors['anime_response_data_dict'][anime_id] = e.message_dict

            if previous_anime_response is None:
                anime_response.anime_id = anime_id
                anime_responses_to_add.append(anime_response)

        if validation_errors:
            return JsonErrorResponse({'validation': validation_errors}, HTTPStatus.BAD_REQUEST)

        response.save()
        for anime_response in anime_responses_to_add:
            anime_response.response = response
        AnimeResponse.objects.bulk_create(anime_responses_to_add)
        AnimeResponse.objects.bulk_update(anime_responses_to_update.values(), ['watching', 'underwatched', 'score', 'expectations'])
        if previous_response:
            existing_anime_response_queryset.exclude(anime_id__in=anime_response_data_dict.keys()).delete()

        #########################
        #########################
        

        username_hash = get_username_hash(request.user)
        MtmUserResponse.objects.update_or_create(
            username_hash=username_hash, survey=survey,
            defaults={
                'response': response if link_response_to_user else None,
            }
        )

        if link_response_to_user:
            return JsonResponse({}, status=HTTPStatus.NO_CONTENT)
        else:
            return JsonResponse({'response_id': response.public_id})



def try_get_previous_response(user: User, response_public_id: Optional[str], survey: Survey) -> tuple[Optional[Response], bool, bool]:
    username_hash = get_username_hash(user)
    mtmuserresponse_queryset = MtmUserResponse.objects.filter(username_hash=username_hash, survey=survey)

    # If there is a row, the user responded to this survey
    # If there is none, don't load any response, not even from the response's public id if supplied as this is likely not the user's response
    if not mtmuserresponse_queryset.exists():
        return None, False, False
    else:
        # response can be None if the user did not want the response linked to hem
        response = mtmuserresponse_queryset.first().response
        response_was_linked = response is not None

        # If there is no linked response, try to use the response's public id
        if not response_was_linked and response_public_id is not None:
            response = Response.objects.filter(public_id=response_public_id, survey=survey).first()

        return response, response_was_linked, True

def get_username_hash(user: User) -> bytes:
    return sha512(user.username.encode('utf-8')).digest()



@dataclass
class SurveyFromSubmitData(DataBase): # Not a good name
    response_data: ResponseData
    anime_response_data_dict: dict[int, AnimeResponseData]
    is_response_linked_to_user: bool

    @classproperty
    def dict_field_parsers(cls) -> dict[str, Callable[[Any], Any]]:

        # Parses the dict and filters empty anime responses
        def anime_response_data_dict_parser(d: dict[str, dict[str, Any]]) -> dict[int, AnimeResponseData]:
            result: dict[int, AnimeResponseData] = {}
            for anime_id_str, anime_response_json_data in d.items():
                anime_response_data = AnimeResponseData.from_dict(anime_response_json_data)
                if anime_response_data.contains_data:
                    result[int(anime_id_str)] = anime_response_data
            return result

        parsers = super().dict_field_parsers
        parsers.update({
            'response_data': (lambda d: ResponseData.from_dict(d)),
            'anime_response_data_dict': anime_response_data_dict_parser,
        })
        return parsers

@dataclass
class ResponseData(DataBase):
    age: Optional[int] = None
    gender: Optional[str] = None

    @staticmethod
    def from_model(model: Response) -> ResponseData:
        return ResponseData(
            age=model.age,
            gender=model.gender,
        )
    
    def to_model(self, model: Optional[Response]=None) -> Response:
        if model is None:
            return Response(
                age=self.age,
                gender=self.gender
            )
        else:
            model.age = self.age
            model.gender = self.gender
            return model

@dataclass
class AnimeResponseData(DataBase):
    score: Optional[int] = None
    watching: bool = False
    underwatched: bool = False
    expectations: Optional[str] = None

    @property
    def contains_data(self) -> bool:
        return self.score is not None or self.watching or self.underwatched or self.expectations is not None

    @staticmethod
    def from_model(model: AnimeResponse) -> AnimeResponseData:
        return AnimeResponseData(
            score=model.score,
            watching=model.watching,
            underwatched=model.underwatched,
            expectations=model.expectations,
        )

    def to_model(self, model: Optional[AnimeResponse]=None) -> AnimeResponse:
        if model is None:
            return AnimeResponse(
                score=self.score,
                watching=self.watching if self.watching is not None else False,
                underwatched=self.underwatched if self.underwatched is not None else False,
                expectations=self.expectations,
            )
        else:
            model.score = self.score
            model.watching = self.watching if self.watching is not None else False
            model.underwatched = self.underwatched if self.underwatched is not None else False
            model.expectations = self.expectations
            return model

@dataclass
class SurveyFormData(DataBase):
    survey: SurveyData
    response_data: ResponseData
    anime_data_dict: dict[int, AnimeData]
    anime_response_data_dict: dict[int, AnimeResponseData]
    is_anime_new_dict: dict[int, bool]
    is_response_linked_to_user: bool
