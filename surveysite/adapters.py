from allauth.account.adapter import DefaultAccountAdapter
from django.http.request import HttpRequest
from django.urls.base import reverse

class CustomAccountAdapter(DefaultAccountAdapter):
    def get_login_redirect_url(self, request: HttpRequest):
        return request.COOKIES.get('loginredirecturl', reverse('index'))
