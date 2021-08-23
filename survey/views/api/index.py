from datetime import datetime
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.generic import View
from survey.models import Anime, Image, Survey
from survey.util.data import ImageData, ResultsType, SurveyAnimeData, SurveyData, json_encoder_factory, AnimeData
from survey.util.survey import get_survey_anime
from survey.views.results import ResultsGenerator


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
                anime_series_results, _ = ResultsGenerator(survey).get_anime_results_data()
                anime_results = {
                    resultstype.value: get_top_results(anime_series_results, resultstype, 2)
                    for resultstype in resultstype_list
                }
            else:
                anime_list, _, _ = get_survey_anime(survey)
                anime_images = Image.objects.filter(anime__in=anime_list).order_by('?')[:12]
                anime_images = [ImageData.from_model(image) for image in anime_images]

            response.append(SurveyData(
                year         = survey.year,
                season       = survey.season,
                is_preseason = survey.is_preseason,
                opening_epoch_time = survey.opening_time.timestamp() * 1000,
                closing_epoch_time = survey.closing_time.timestamp() * 1000,
                anime_results = anime_results,
                anime_images  = anime_images,
            ))
        
        return JsonResponse(response, encoder=jsonEncoder, safe=False)


def get_top_results(results: dict[Anime, dict[ResultsType, float]], resultstype: ResultsType, count: int, descending: bool=True):
    sorted_results = sorted(
        results.items(),
        reverse=descending,
        key=lambda item: item[1][resultstype]
    )[:count]

    return [
                      # If this does one query per anime when gathering images, then check if this can be optimized
        SurveyAnimeData(anime=AnimeData.from_model(anime), result=anime_results[resultstype])
        for (anime, anime_results) in sorted_results
    ]
