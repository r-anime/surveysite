from django.http.response import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.generic import View
from survey.models import MissingAnime
from survey.util import AnimeUtil

missinganime_admin_perms = [
    'survey.{}_{}'.format(perm_type, perm_model)
    for perm_type in ['add', 'change', 'delete', 'view']
    for perm_model in ['anime', 'animename', 'image', 'video', 'missinganime']
]

@method_decorator([never_cache], name='dispatch')
class NotificationsView(View):
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({})

        missinganime_queryset = MissingAnime.objects.filter(user=request.user, user_has_read=False, admin_has_reviewed=True)
        missinganime_queryset.update(user_has_read=True)

        response = {
            'missingAnimeList': [{
                    'submittedName': missinganime.name,
                    'submittedLink': missinganime.link,
                    'nameList': AnimeUtil.get_name_list(missinganime.anime) if missinganime.anime else [],
                    'surveyName': str(missinganime.survey),
                    'reason': missinganime.reason,
                } for missinganime in missinganime_queryset
            ],
        }

        if request.user.is_staff and request.user.has_perms(missinganime_admin_perms):
            unreviewed_missinganime_queryset = MissingAnime.objects.filter(admin_has_reviewed=False)
            response['unreviewedMissingAnimeList'] = [{
                    'submittedName': missinganime.name,
                    'submittedLink': missinganime.link,
                    'submittedDescription': missinganime.description,
                    'surveyName': str(missinganime.survey),
                } for missinganime in unreviewed_missinganime_queryset
            ]

        return JsonResponse(response)
