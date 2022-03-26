from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from surveysite.views import IndexView, SurveyLoginView, SurveyLogoutView

urlpatterns = [
    path('api/', include('survey.urls')),
    path('admin/', admin.site.urls),
    path('accounts/login/', view=SurveyLoginView.as_view(), name='login'),
    path('accounts/logout/', view=SurveyLogoutView.as_view(), name='logout'),
    path('accounts/', include('allauth.urls')),
    re_path(r'^(?!files|static|api).*$', IndexView.as_view(), name='index'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
