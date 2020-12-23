from allauth.account.views import LoginView, LogoutView
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.http import Http404

class SurveyLoginView(LoginView):
    template_name = 'survey/login.html'

survey_login_view = SurveyLoginView.as_view()

def survey_logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect(request.POST['next'])
    else:
        return Http404()
