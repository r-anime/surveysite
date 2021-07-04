from logging import exception
from django.contrib import messages
from django.shortcuts import redirect
from survey.models import Survey
from survey.util import SurveyUtil

class RequireSurveyOngoingMixin:
    def dispatch(self, request, *args, **kwargs):
        if not hasattr(self, 'get_survey'):
            raise exception('RequireSurveyOngoingMixin requires the use of SurveyMixin.')

        survey = self.get_survey()
        if survey.state != Survey.State.ONGOING and not request.user.is_staff:
            messages.error(request, str(survey) + ' is closed!')
            return redirect('survey:index')
        return super().dispatch(request, *args, **kwargs)


class SurveyMixin:
    __survey = None
    __anime_list_tuple = None

    def get_anime_lists(self):
        """Returns the combined anime list, the anime series list, and the special anime list of the current survey."""
        if not self.__anime_list_tuple:
            self.__anime_list_tuple = SurveyUtil.get_survey_anime(self.get_survey())
        return self.__anime_list_tuple

    def get_survey(self):
        """Returns the survey belonging to the season of the current request."""
        if not self.__survey:
            self.__survey = SurveyUtil.get_survey_or_404(
                year=self.kwargs['year'],
                season=self.kwargs['season'],
                pre_or_post=self.kwargs['pre_or_post'],
            )
        return self.__survey

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['survey'] = self.get_survey()
        context['anime_list'], context['anime_series_list'], context['special_anime_list'] = self.get_anime_lists()
        return context
    

class UserMixin:
    __user_info = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_info'] = self.get_user_info()
        return context

    def get_user_info(self):
        """Gets displayable information about the user. Returns None if the user is not authenticated."""
        if self.__user_info is None:
            if not self.request.user.is_authenticated:
                self.__user_info = {}
            else:
                socialaccount_queryset = self.request.user.socialaccount_set.all()
                reddit_account_queryset = socialaccount_queryset.filter(provider='reddit')
                if reddit_account_queryset.count() == 1:
                    account = reddit_account_queryset[0]
                    username = account.uid
                    image = account.extra_data['icon_img']
                elif socialaccount_queryset.count() > 1:
                    account = self.request.user.socialaccount_set.all()[0]
                    username = account.uid
                    image = None
                else:
                    username = self.request.user.username
                    image = None

                self.__user_info = {
                    'username': username,
                    'image': image,
                }

        return self.__user_info
