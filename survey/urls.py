from django.urls import path, include
from django.shortcuts import redirect
from . import views
from .resultview import ResultsView, FullResultsView

app_name = 'survey'

def favicon_redirect(request):
    return redirect('/static/favicon/favicon.ico')

survey_patterns = [
    path('<int:year>/<int:season>/<pre_or_post>/', views.form, name='form'),
    path('<int:year>/<int:season>/<pre_or_post>/results/', ResultsView.as_view(), name='results'),
    path('<int:year>/<int:season>/<pre_or_post>/fullresults/', FullResultsView.as_view(), name='fullresults'),
]

urlpatterns = [
    path('', views.index, name='index'),
    path('survey/', include(survey_patterns)),
    path('favicon.ico', favicon_redirect),
]
