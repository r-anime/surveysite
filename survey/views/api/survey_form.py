from survey.util.survey import get_survey_or_404, get_survey_anime
from dataclasses import dataclass
from survey.util.data import AnimeData, SurveyData, json_encoder_factory, DataBase
from django.http import JsonResponse
from django.views.generic import View

class SurveyFormApi(View):
    def get(self, request, *args, **kwargs):
        jsonEncoder = json_encoder_factory()

        survey = get_survey_or_404(
            year=self.kwargs['year'],
            season=self.kwargs['season'],
            pre_or_post=self.kwargs['pre_or_post'],
        )

        anime_list, _, _ = get_survey_anime(survey)
        
        response = SurveyFormData(
            survey=SurveyData.from_model(survey),
            anime_list=[AnimeData.from_model(anime) for anime in anime_list]
        )

        return JsonResponse(response, encoder=jsonEncoder, safe=False)

@dataclass
class SurveyFormData(DataBase):
    survey: SurveyData
    anime_list: list[AnimeData]
