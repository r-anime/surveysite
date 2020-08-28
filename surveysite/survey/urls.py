from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('<year_season>/<pre_or_post>/', views.form, name='form'),
    path('<year_season>/<pre_or_post>/results/', views.results, name='results'),
]
