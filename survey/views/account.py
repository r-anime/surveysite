from allauth.account.views import LoginView
from django.views.generic import View
from django.contrib.auth import logout
from django.shortcuts import redirect

class SurveyLoginView(LoginView):
    template_name = 'survey/login.html'

class SurveyLogoutView(View):
    def post(self, request, *args, **kwargs):
        logout(request)
        return redirect(request.POST['next'])
