from django.urls import path, include
from . import views

app_name = 'survey'

survey_patterns = [
    path('<int:year>/<int:season>/<pre_or_post>/', views.form, name='form'),
    path('<int:year>/<int:season>/<pre_or_post>/results/', views.results, name='results'),
    path('<int:year>/<int:season>/<pre_or_post>/submit/', views.submit, name='submit'),
]

urlpatterns = [
    path('', views.index, name='index'),
    path('survey/', include(survey_patterns))
]
