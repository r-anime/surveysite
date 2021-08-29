from survey.util.survey import get_survey_or_404
from survey.util.data import SurveyData, json_encoder_factory
from django.http import JsonResponse
from django.views.generic import View

class SurveyApi(View):
    def get(self, request, *args, **kwargs):
        jsonEncoder = json_encoder_factory()

        survey = get_survey_or_404(
            year=self.kwargs['year'],
            season=self.kwargs['season'],
            pre_or_post=self.kwargs['pre_or_post'],
        )

        response = SurveyData(
            year=survey.year,
            season=self.kwargs['season'],
            is_preseason=survey.is_preseason,
            opening_epoch_time=survey.opening_time.timestamp()*1000,
            closing_epoch_time=survey.closing_time.timestamp()*1000,
        )

        return JsonResponse(response, encoder=jsonEncoder, safe=False)
