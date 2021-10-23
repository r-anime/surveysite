from django.contrib.auth.decorators import login_required
from django.http.request import HttpRequest
from django.http.response import JsonResponse
from django.utils.decorators import method_decorator
from django.views.generic import View
from http import HTTPStatus
from survey.models import Survey
from survey.util.data import AnimeData, json_encoder_factory
from survey.util.http import JsonErrorResponse
from survey.util.results import ResultsGenerator
from survey.util.survey import get_survey_anime, get_survey_or_404

class SurveyResultsApi(View):
    def get(self, request: HttpRequest, *args, **kwargs):
        survey = get_survey_or_404(
            year=self.kwargs['year'],
            season=self.kwargs['season'],
            pre_or_post=self.kwargs['pre_or_post'],
        )

        if survey.state == Survey.State.UPCOMING:
            return JsonErrorResponse('This survey is not open yet!', HTTPStatus.FORBIDDEN)
        elif survey.state == Survey.State.ONGOING and not request.user.is_staff:
            return JsonErrorResponse('This survey is still ongoing!', HTTPStatus.FORBIDDEN)

        survey_results = ResultsGenerator(survey).get_anime_results_data()

        survey_anime_queryset, _, _ = get_survey_anime(survey)
        survey_anime_data_list = {anime.id: AnimeData.from_model(anime) for anime in survey_anime_queryset}

        json_encoder = json_encoder_factory()
        return JsonResponse({'results': survey_results, 'anime': survey_anime_data_list}, encoder=json_encoder, safe=False)
