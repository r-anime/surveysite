from survey.util.results import ResultsType
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.generic import View
from survey.models import Survey
from survey.util.data import json_encoder_factory, AnimeData
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

        response = {}
        for survey in survey_list:
            if survey.year not in response:
                response[survey.year] = {}
            if survey.season not in response[survey.year]:
                response[survey.year][survey.season] = {}

            anime_series_results, _ = ResultsGenerator(survey).get_anime_results_data()
            results_sorted_by_popularity = sorted(anime_series_results.items(), reverse=True, key=lambda item: item[1][ResultsType.POPULARITY])[:2]
            results_sorted_by_score      = sorted(anime_series_results.items(), reverse=True, key=lambda item: item[1][ResultsType.SCORE     ])[:2]
            response[survey.year][survey.season][survey.is_preseason] = {
                'highest_popularity': [{'anime': AnimeData.from_model(anime), 'popularity': results[ResultsType.POPULARITY]} for (anime, results) in results_sorted_by_popularity],
                'highest_score':      [{'anime': AnimeData.from_model(anime), 'score':      results[ResultsType.SCORE     ]} for (anime, results) in results_sorted_by_score     ],
            }
        
        # response: {
        #   year: {
        #     season: {
        #       is_preseason: {
        #         highest_popularity: [
        #           anime: AnimeData,
        #           popularity: float
        #         ],
        #         highest_score: [
        #           anime: AnimeData,
        #           score: float
        #         ]
        # }}}}
        return JsonResponse(response, encoder=jsonEncoder)
