from django.urls import path
from survey.views.api.index import IndexApi
from survey.views.api.survey_form import SurveyFormApi
from survey.views.api.survey_missing_anime import SurveyMissingAnimeApi
from survey.views.api.survey_results import SurveyResultsApi
from survey.views.api.user import UserApi

app_name = 'survey'

urlpatterns = [
    path('index/', IndexApi.as_view()),
    path('user/', UserApi.as_view()),
    path('survey/<int:year>/<int:season>/<pre_or_post>/', SurveyFormApi.as_view()),
    path('survey/<int:year>/<int:season>/<pre_or_post>/missinganime/', SurveyMissingAnimeApi.as_view()),
    path('survey/<int:year>/<int:season>/<pre_or_post>/results/', SurveyResultsApi.as_view()),
]
