from __future__ import annotations
from dataclasses import dataclass
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.generic import View
from survey.models import Anime, Image, Survey
from survey.util.data import DataBase, ImageData, ResultsType, SurveyData, json_encoder_factory, AnimeData
from survey.util.survey import get_survey_anime
from survey.views.results import ResultsGenerator
from typing import Optional


class IndexApi(View):
    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        year_param = request.GET.get('year', '')
        try:
            year = int(year_param) if year_param else None
        except ValueError:
            return JsonResponse({})
        
        survey_list: list[Survey] = list(Survey.objects.filter(year=year) if year else Survey.objects.all())
        jsonEncoder = json_encoder_factory()

        resultstype_list = [ResultsType.POPULARITY, ResultsType.SCORE]
        response = []
        for survey in survey_list:
            anime_results = None
            anime_images = None
            if survey.state == Survey.State.FINISHED:
                anime_series_results = ResultsGenerator(survey).get_anime_results_data()
                anime_results = {
                    resultstype.value: get_top_results(anime_series_results, resultstype, 2)
                    for resultstype in resultstype_list
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


def get_top_results(results: dict[int, dict[ResultsType, float]], resultstype: ResultsType, count: int, descending: bool=True):
    sorted_results = sorted(
        results.items(),
        reverse=descending,
        key=lambda item: item[1][resultstype]
    )[:count]

    return [                 # Check how this can be optimized
        IndexSurveyAnimeData(anime=AnimeData.from_model(Anime.objects.get(id=anime_id)), result=anime_results[resultstype])
        for (anime_id, anime_results) in sorted_results
    ]


@dataclass
class IndexSurveyData(SurveyData):
    anime_results: Optional[dict[ResultsType, list[IndexSurveyAnimeData]]]
    anime_images: Optional[list[ImageData]]

    @staticmethod
    def from_model(model: Survey, anime_images: Optional[list[ImageData]], anime_results: Optional[dict[ResultsType, list[IndexSurveyAnimeData]]]) -> IndexSurveyData:
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
