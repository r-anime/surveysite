from dataclasses import dataclass, field
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.generic import View
from survey.util.data import ViewModelBase, json_encoder_factory


@method_decorator(never_cache, name='get')
class UserApi(View):
    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        jsonEncoder = json_encoder_factory()

        if not request.user or not request.user.is_authenticated:
            auth_url = reverse('reddit_login') # Get allauth's Reddit provider login URL (allauth.socialaccount.providers.RedditProvider.get_login_url(..))
            return JsonResponse(AnonymousUserViewModel(
                authentication_url=auth_url,
            ), encoder=jsonEncoder, safe=False)

        reddit_account_queryset = self.request.user.socialaccount_set.filter(provider='reddit')
        profile_picture_url = reddit_account_queryset[0].extra_data['icon_img'] if reddit_account_queryset else None
            
        return JsonResponse(AuthenticatedUserViewModel(
            username=request.user.first_name if request.user.first_name else request.user.username,
            profile_picture_url=profile_picture_url,
            is_staff=request.user.is_staff,
        ), encoder=jsonEncoder, safe=False)


@dataclass
class UserViewModel(ViewModelBase):
    authenticated: bool

@dataclass
class AnonymousUserViewModel(UserViewModel):
    authenticated: bool = field(default=False, init=False)
    authentication_url: str

@dataclass
class AuthenticatedUserViewModel(UserViewModel):
    authenticated: bool = field(default=True, init=False)
    is_staff: bool
    username: str
    profile_picture_url: str