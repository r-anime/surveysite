from survey.util.results import ResultsType
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.generic import View
from survey.models import Survey
from survey.util.data import SurveyAnimeData, SurveyData, json_encoder_factory, AnimeData
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

        response = []
        for survey in survey_list:
            anime_series_results, _ = ResultsGenerator(survey).get_anime_results_data()
            results_sorted_by_popularity = sorted(anime_series_results.items(), reverse=True, key=lambda item: item[1][ResultsType.POPULARITY])[:2]
            results_sorted_by_score      = sorted(anime_series_results.items(), reverse=True, key=lambda item: item[1][ResultsType.SCORE     ])[:2]
            response.append(SurveyData(
                year         = survey.year,
                season       = survey.season,
                is_preseason = survey.is_preseason,
                most_popular_anime = [SurveyAnimeData(anime = AnimeData.from_model(anime), result = results[ResultsType.POPULARITY]) for (anime, results) in results_sorted_by_popularity],
                best_anime         = [SurveyAnimeData(anime = AnimeData.from_model(anime), result = results[ResultsType.SCORE     ]) for (anime, results) in results_sorted_by_score     ],
            ))
        
        return JsonResponse(response, encoder=jsonEncoder, safe=False)
