from __future__ import annotations
from dataclasses import dataclass
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.http.response import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.utils.functional import classproperty
from django.views.generic import View
from hashlib import sha512
from http import HTTPStatus
import json
from survey.models import AnimeResponse, MtmUserResponse, Response, Survey
from survey.util.anime import anime_is_continuing
from survey.util.data import AnimeData, SurveyData, json_encoder_factory, DataBase
from survey.util.survey import get_survey_or_404, get_survey_anime
from typing import Any, Callable, Optional

class SurveyFormApi(View):
    def get(self, request, *args, **kwargs):
        jsonEncoder = json_encoder_factory()

        survey = get_survey_or_404(
            year=self.kwargs['year'],
            season=self.kwargs['season'],
            pre_or_post=self.kwargs['pre_or_post'],
        )

        previous_response, has_user_responded = try_get_previous_response(self.request.user, survey)
        if has_user_responded and not previous_response:
            return HttpResponseForbidden('You already respoded to this survey!')

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
        )

        return JsonResponse(response, encoder=jsonEncoder, safe=False)

    def post(self, request, *args, **kwargs):
        json_data: dict[str, dict[str, Any]] = json.loads(request.body)

        try:
            submit_data = SurveyFromSubmitData.from_dict(json_data)
        except KeyError:
            return HttpResponseBadRequest('Request data is invalid')

        response_data = submit_data.response_data
        anime_response_data_dict = submit_data.anime_response_data_dict
        survey = get_survey_or_404(
            year=self.kwargs['year'],
            season=self.kwargs['season'],
            pre_or_post=self.kwargs['pre_or_post'],
        )

        print(response_data)
        print(anime_response_data_dict)

        return HttpResponse(status=HTTPStatus.NO_CONTENT)


def try_get_previous_response(user: User, survey: Survey) -> tuple[Response, bool]:
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
    response_is_linked_to_user: bool

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

@dataclass
class AnimeResponseData(DataBase):
    score: Optional[int] = None
    watching: Optional[bool] = None
    underwatched: Optional[bool] = None
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
            # Bit jank, but since the neutral answer is stored in the DB as an empty string, this otherwise goes wrong on the front-end
            expectations=model.expectations if model.expectations else None,
        )

@dataclass
class SurveyFormData(DataBase):
    survey: SurveyData
    response_data: ResponseData
    anime_data_dict: dict[int, AnimeData]
    anime_response_data_dict: dict[int, AnimeResponseData]

    is_anime_new_dict: dict[int, bool]
