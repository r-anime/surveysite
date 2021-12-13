from allauth.socialaccount.providers import registry as auth_provider_registry
from dataclasses import dataclass
from typing import Optional
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.generic import View
from survey.util.data import DataBase, json_encoder_factory


class UserApi(View):
    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        jsonEncoder = json_encoder_factory()

        if not request.user or not request.user.is_authenticated:
            auth_provider = auth_provider_registry.by_id('reddit', request)
            auth_url = auth_provider.get_login_url(request)
            return JsonResponse(UserData(
                authenticated=False,
                authentication_url=auth_url,
            ), encoder=jsonEncoder, safe=False)

        reddit_account_queryset = self.request.user.socialaccount_set.filter(provider='reddit')
        profile_picture = reddit_account_queryset[0].extra_data['icon_img'] if reddit_account_queryset else None
            
        return JsonResponse(UserData(
            authenticated=True,
            username=request.user.first_name if request.user.first_name else request.user.username,
            profile_picture=profile_picture,
        ), encoder=jsonEncoder, safe=False)


@dataclass
class UserData(DataBase):
    authenticated: bool
    username: Optional[str] = None
    profile_picture: Optional[str] = None
    authentication_url: Optional[str] = None
