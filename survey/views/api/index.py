from __future__ import annotations
from dataclasses import dataclass
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.generic import View
import math
from survey.models import Anime, Image, Survey
from survey.util.data import DataBase, ImageData, ResultType, SurveyData, json_encoder_factory, AnimeData
from survey.util.results import ResultsGenerator
from survey.util.survey import get_survey_anime
from typing import Optional


class IndexApi(View):
    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        year_param = request.GET.get('year', '')
        try:
            year = int(year_param) if year_param else None
        except ValueError:
            return JsonResponse({})
        
        survey_list: list[Survey] = list(Survey.objects.filter(year=2020, season=3)) #list(Survey.objects.filter(year=year) if year else Survey.objects.all())
        jsonEncoder = json_encoder_factory()

        resulttype_list = [ResultType.POPULARITY, ResultType.SCORE]
        response = []
        for survey in survey_list:
            anime_results = None
            anime_images = None
            if survey.state == Survey.State.FINISHED:
                anime_results = ResultsGenerator(survey).get_anime_results_data()
                anime_results = {
                    resulttype.value: get_top_results(anime_results, resulttype, 2)
                    for resulttype in resulttype_list
                }
            else:
                anime_list, _, _ = get_survey_anime(survey)
                anime_images = Image.objects.filter(anime__in=anime_list).order_by('?')[:12]
                anime_images = [ImageData.from_model(image) for image in anime_images]

            response.append(IndexSurveyData.from_model(
                model=survey,
                anime_images=anime_images,
                anime_results=anime_results,
            ))

        return JsonResponse(response, encoder=jsonEncoder, safe=False)


def get_top_results(results: dict[int, dict[ResultType, float]], resulttype: ResultType, count: int, descending: bool=True):
    # Remove anime below the popularity threshold, and anime with a result value of NaN or infinite
    sorted_results = [
        (anime_id, anime_results)
        for (anime_id, anime_results) in results.items()
        if anime_results[ResultType.POPULARITY] > 0.02 and math.isfinite(anime_results[resulttype])
    ]

    # Sort all anime by the given result type
    sorted_results = sorted(
        sorted_results,
        reverse=descending,
        key=lambda item: item[1][resulttype]
    )

    return [                 # Check how this can be optimized
        IndexSurveyAnimeData(anime=AnimeData.from_model(Anime.objects.get(id=anime_id)), result=anime_results[resulttype])
        for (anime_id, anime_results) in sorted_results[:count]
    ]


@dataclass
class IndexSurveyData(SurveyData):
    anime_results: Optional[dict[ResultType, list[IndexSurveyAnimeData]]]
    anime_images: Optional[list[ImageData]]

    @staticmethod
    def from_model(model: Survey, anime_images: Optional[list[ImageData]], anime_results: Optional[dict[ResultType, list[IndexSurveyAnimeData]]]) -> IndexSurveyData:
        survey_data = SurveyData.from_model(model)
        return IndexSurveyData(
            year=survey_data.year,
            season=survey_data.season,
            is_preseason=survey_data.is_preseason,
            opening_epoch_time=survey_data.opening_epoch_time,
            closing_epoch_time=survey_data.closing_epoch_time,
            anime_images=anime_images,
            anime_results=anime_results,
        )

@dataclass
class IndexSurveyAnimeData(DataBase):
    anime: AnimeData
    result: float
