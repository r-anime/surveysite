from django.urls import path
from . import views

app_name = 'survey'
urlpatterns = [
    path('', views.index, name='index'),
    path('<year>/<season>/<pre_or_post>/', views.survey, name='survey'),
    path('<year>/<season>/<pre_or_post>/submit/', views.submit, name='submit'),
]
