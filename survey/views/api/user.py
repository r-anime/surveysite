from django.contrib.auth.models import User
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.generic import View
from survey.util.data import UserData, json_encoder_factory


class UserApi(View):
    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        jsonEncoder = json_encoder_factory()

        if not request.user or not request.user.is_authenticated:
            JsonResponse()
            return JsonResponse(UserData(authenticated=False), encoder=jsonEncoder)

        reddit_account_queryset = self.request.user.socialaccount_set.filter(provider='reddit')
        profile_picture = reddit_account_queryset[0].extra_data['icon_img'] if reddit_account_queryset else None
            
        return JsonResponse(UserData(
            authenticated=True,
            username=request.user.first_name if request.user.first_name else request.user.username,
            profile_picture=profile_picture
        ), encoder=jsonEncoder, safe=False)
