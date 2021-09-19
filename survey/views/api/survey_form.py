from __future__ import annotations
from dataclasses import dataclass
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.http.request import HttpRequest
from django.utils.functional import classproperty
from django.views.generic import View
from hashlib import sha512
from http import HTTPStatus
import json
import logging
from survey.models import AnimeResponse, MtmUserResponse, Response, Survey
from survey.util.anime import anime_is_continuing
from survey.util.data import AnimeData, SurveyData, json_encoder_factory, DataBase
from survey.util.http import JsonErrorResponse
from survey.util.survey import get_survey_or_404, get_survey_anime
from typing import Any, Callable, Optional

class SurveyFormApi(View):
    def get(self, request: HttpRequest, *args, **kwargs):
        jsonEncoder = json_encoder_factory()

        survey = get_survey_or_404(
            year=self.kwargs['year'],
            season=self.kwargs['season'],
            pre_or_post=self.kwargs['pre_or_post'],
        )

        previous_response, has_user_responded = try_get_previous_response(request.user, survey)
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
            is_response_linked_to_user=previous_response is not None,
        )

        return JsonResponse(response, encoder=jsonEncoder, safe=False)

    def post(self, request: HttpRequest, *args, **kwargs):
        survey = get_survey_or_404(
            year=self.kwargs['year'],
            season=self.kwargs['season'],
            pre_or_post=self.kwargs['pre_or_post'],
        )
        
        previous_response, has_user_responded = try_get_previous_response(request.user, survey)
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

        response = response_data.to_model(previous_response)
        try:
            response.full_clean()
        except ValidationError as e:
            # TODO: Properly handle errors
            print(e.error_dict)
            raise e

        if previous_response is None:
            response.survey = survey

        new_anime_response_list: list[AnimeResponse] = []
        existing_anime_response_list: list[AnimeResponse] = []
        for anime_id, anime_response_data in anime_response_data_dict.items():
            anime_response_queryset = AnimeResponse.objects.filter(response=previous_response, anime_id=anime_id) if previous_response else None
            previous_anime_response = None
            if anime_response_queryset and anime_response_queryset.count() == 1:
                previous_anime_response = anime_response_queryset.first()

            anime_response = anime_response_data.to_model(previous_anime_response)
            try:
                anime_response.full_clean()
            except ValidationError as e:
                # TODO: Properly handle errors
                print(e.error_dict)
                raise e

            if previous_anime_response is None:
                anime_response.anime_id = anime_id
                new_anime_response_list.append(anime_response)
            else:
                existing_anime_response_list.append(anime_response)

        response.save()
        for anime_response in new_anime_response_list:
            anime_response.response = response
        AnimeResponse.objects.bulk_create(new_anime_response_list)
        AnimeResponse.objects.bulk_update(existing_anime_response_list, ['watching', 'underwatched', 'score', 'expectations'])

        username_hash = get_username_hash(request.user)
        MtmUserResponse.objects.update_or_create(
            username_hash=username_hash, survey=survey,
            defaults={
                'response': response if link_response_to_user else None,
            }
        )

        return JsonResponse({}, status=HTTPStatus.NO_CONTENT)



def try_get_previous_response(user: User, survey: Survey) -> tuple[Optional[Response], bool]:
    username_hash = get_username_hash(user)
    mtmuserresponse_queryset = MtmUserResponse.objects.filter(username_hash=username_hash, survey=survey)

    # If there is a row, the user responded to this survey
    # No need to check whether there are multiple entries in the queryset as there's a uniqueness constraint on username_hash and survey
    if not mtmuserresponse_queryset.exists():
        return None, False
    else:
        # response can be None if the user did not want the response linked to hem
        response = mtmuserresponse_queryset.first().response
        return response, True

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
        def anime_response_data_dict_parser(d: dict[int, dict[str, Any]]) -> dict[int, AnimeResponseData]:
            result: dict[int, AnimeResponseData] = {}
            for anime_id, anime_response_json_data in d.items():
                anime_response_data = AnimeResponseData.from_dict(anime_response_json_data)
                if anime_response_data.contains_data:
                    result[anime_id] = anime_response_data
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
        #print(model._meta.get_fields())
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
