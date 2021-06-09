from django.contrib.auth.decorators import login_required
from django.http.response import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.generic import View
from survey.models import MissingAnime
from survey.util import AnimeUtil

@method_decorator([never_cache, login_required], name='dispatch')
class NotificationsView(View):
    def get(self, request, *args, **kwargs):
        missinganime_queryset = MissingAnime.objects.filter(user=request.user, user_has_read=False, admin_has_reviewed=True)
        missinganime_queryset.update(user_has_read=True)
        
        response = {
            'missingAnimeList': [{
                    'submittedName': missinganime.name,
                    'submittedLink': missinganime.link,
                    'nameList': AnimeUtil.get_name_list(missinganime.anime) if missinganime.anime else [],
                    'surveyName': str(missinganime.survey),
                } for missinganime in missinganime_queryset
            ]
        }
        return JsonResponse(response)