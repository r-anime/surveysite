"""surveysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.http.response import HttpResponse
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from survey.views.account import SurveyLoginView, SurveyLogoutView
from django.shortcuts import render

urlpatterns = [
    path('api/', include('survey.urls')),
    path('admin/', admin.site.urls),
    path('accounts/login/', view=SurveyLoginView.as_view(), name='login'),
    path('accounts/logout/', view=SurveyLogoutView.as_view(), name='logout'),
    path('accounts/', include('allauth.urls')),
    re_path(r'.*', lambda request: render(request, 'index.html')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
