from django.urls import path, include
from django.shortcuts import redirect
from survey.views.index import IndexView
from survey.views.form import FormView
from survey.views.results import ResultsView, FullResultsView

app_name = 'survey'

def favicon_redirect(request):
    return redirect('/static/favicon/favicon.ico')

survey_patterns = [
    path('<int:year>/<int:season>/<pre_or_post>/', FormView.as_view(), name='form'),
    path('<int:year>/<int:season>/<pre_or_post>/results/', ResultsView.as_view(), name='results'),
    path('<int:year>/<int:season>/<pre_or_post>/fullresults/', FullResultsView.as_view(), name='fullresults'),
]

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('survey/', include(survey_patterns)),
    path('favicon.ico', favicon_redirect),
]
