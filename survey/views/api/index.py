from __future__ import annotations
from dataclasses import dataclass
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.generic import View
import math
from survey.models import Anime, Image, Survey
from survey.util.data import ViewModelBase, ImageViewModel, ResultType, SurveyViewModel, json_encoder_factory, AnimeViewModel
from survey.util.results import ResultsGenerator
from survey.util.survey import get_survey_anime
from typing import Optional


# Don't cache the index, we perform caching on the computationally-intensive part of this (gathering survey results data),
# and we don't want users to see surveys still being closed/open when they've just opened/closed
@method_decorator(never_cache, name='get')
class IndexApi(View):
    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        year_param = request.GET.get('year', '')
        try:
            year = int(year_param) if year_param else None
        except ValueError:
            return JsonResponse({})
        
        survey_list: list[Survey] = list(Survey.objects.filter(year=year) if year else Survey.objects.all())
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
                anime_images = [ImageViewModel.from_model(image) for image in anime_images]

            response.append(IndexSurveyViewModel.from_model(
                model=survey,
                anime_images=anime_images,
                anime_results=anime_results,
            ))

        return JsonResponse(response, encoder=jsonEncoder, safe=False)


def get_top_results(results: dict[int, dict[ResultType, float]], resulttype: ResultType, count: int, descending: bool=True):
    # Only keep anime above the popularity threshold, and with a valid result value
    sorted_results = [
        (anime_id, anime_results)
        for (anime_id, anime_results) in results.items()
        if anime_results[ResultType.POPULARITY] is not None
           and anime_results[ResultType.POPULARITY] > 0.02
           and anime_results[resulttype] is not None
    ]

    # Sort all anime by the given result type
    sorted_results = sorted(
        sorted_results,
        reverse=descending,
        key=lambda item: item[1][resulttype]
    )

    return [                 # Check how this can be optimized
        IndexSurveyAnimeViewModel(anime=AnimeViewModel.from_model(Anime.objects.get(id=anime_id)), result=anime_results[resulttype])
        for (anime_id, anime_results) in sorted_results[:count]
    ]


@dataclass
class IndexSurveyViewModel(SurveyViewModel):
    anime_results: Optional[dict[ResultType, list[IndexSurveyAnimeViewModel]]]
    anime_images: Optional[list[ImageViewModel]]

    @staticmethod
    def from_model(model: Survey, anime_images: Optional[list[ImageViewModel]], anime_results: Optional[dict[ResultType, list[IndexSurveyAnimeViewModel]]]) -> IndexSurveyViewModel:
        survey_data = SurveyViewModel.from_model(model)
        return IndexSurveyViewModel(
            year=survey_data.year,
            season=survey_data.season,
            is_preseason=survey_data.is_preseason,
            opening_epoch_time=survey_data.opening_epoch_time,
            closing_epoch_time=survey_data.closing_epoch_time,
            anime_images=anime_images,
            anime_results=anime_results,
        )

@dataclass
class IndexSurveyAnimeViewModel(ViewModelBase):
    anime: AnimeViewModel
    result: float
