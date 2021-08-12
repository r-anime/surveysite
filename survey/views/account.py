from allauth.socialaccount.providers import registry
from django.views.generic import View
from django.contrib.auth import logout
from django.shortcuts import redirect

class SurveyLoginView(View):
    def get(self, request, *args, **kwargs):
        provider = registry.by_id('reddit', request)
        url = provider.get_login_url(request, next=request.GET.get('next', None))
        return redirect(url)

class SurveyLogoutView(View):
    def post(self, request, *args, **kwargs):
        logout(request)
        return redirect(request.POST['next'])
