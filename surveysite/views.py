from allauth.socialaccount.providers import registry
from django.contrib.auth import logout
from django.http.request import HttpRequest
from django.shortcuts import redirect, render
from django.urls.base import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.generic.base import View

@method_decorator(ensure_csrf_cookie, name='dispatch')
class IndexView(View):
    def get(self, request: HttpRequest, *args, **kwargs):
        return render(request, 'index.html')

class SurveyLoginView(View):
    def get(self, request: HttpRequest, *args, **kwargs):
        provider = registry.by_id('reddit', request)
        url = provider.get_login_url(request)
        return redirect(url)

class SurveyLogoutView(View):
    def post(self, request: HttpRequest, *args, **kwargs):
        logout(request)
        return redirect(request.POST.get('next', reverse('index')))
