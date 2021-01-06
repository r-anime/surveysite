from django.urls import path, include
from . import views
from .resultview import ResultsView

app_name = 'survey'

survey_patterns = [
    path('<int:year>/<int:season>/<pre_or_post>/', views.form, name='form'),
    path('<int:year>/<int:season>/<pre_or_post>/results/', ResultsView.as_view(), name='results'),
    path('<int:year>/<int:season>/<pre_or_post>/submit/', views.submit, name='submit'),
]

urlpatterns = [
    path('', views.index, name='index'),
    path('survey/', include(survey_patterns))
]
