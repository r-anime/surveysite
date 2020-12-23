from allauth.account.views import LoginView

class SurveyLoginView(LoginView):
    template_name = 'survey/login.html'

survey_login_view = SurveyLoginView.as_view()