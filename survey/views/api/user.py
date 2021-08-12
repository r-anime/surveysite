from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.generic import View

class UserApi(View):
    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if not request.user or not request.user.is_authenticated:
            return JsonResponse({'authenticated': False})
        return JsonResponse({'authenticated': True, 'username': request.user.username})
