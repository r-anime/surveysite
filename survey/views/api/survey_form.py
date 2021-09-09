from __future__ import annotations
from dataclasses import dataclass
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.http.response import HttpResponseForbidden
from django.views.generic import View
from hashlib import sha512
from survey.models import AnimeResponse, MtmUserResponse, Response, Survey
from survey.util.data import AnimeData, SurveyData, json_encoder_factory, DataBase
from survey.util.survey import get_survey_or_404, get_survey_anime
from typing import Optional

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
        anime_response_data_list: list[AnimeResponseData] = []
        for anime in anime_list:
            previous_animeresponse_queryset = AnimeResponse.objects.filter(response=previous_response, anime=anime)
            if previous_animeresponse_queryset and previous_animeresponse_queryset.count() == 1:
                anime_response_data_list.append(AnimeResponseData.from_model(previous_animeresponse_queryset.first()))
            else:
                anime_response_data_list.append(AnimeResponseData(anime_id=anime.id))
        
        response = SurveyFormData(
            survey=SurveyData.from_model(survey),
            anime_data_list=[AnimeData.from_model(anime) for anime in anime_list],
            response_data=response_data,
            anime_response_data_list=anime_response_data_list
        )

        return JsonResponse(response, encoder=jsonEncoder, safe=False)



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
class ResponseData(DataBase):
    age: Optional[int] = None
    gender: Optional[str] = None

    @staticmethod
    def from_model(model: Response) -> ResponseData:
        return ResponseData(
            age=model.age,
            gender=model.gender,
        )

@dataclass
class AnimeResponseData(DataBase):
    anime_id: int
    score: Optional[int] = None
    watching: Optional[bool] = None
    underwatched: Optional[bool] = None
    expectations: Optional[str] = None

    @staticmethod
    def from_model(model: AnimeResponse) -> AnimeResponseData:
        return AnimeResponseData(
            anime_id=model.anime.id,
            score=model.score,
            watching=model.watching,
            underwatched=model.underwatched,
            expectations=model.expectations,
        )

@dataclass
class SurveyFormData(DataBase):
    survey: SurveyData
    response_data: ResponseData
    anime_data_list: list[AnimeData]
    anime_response_data_list: list[AnimeResponseData]
