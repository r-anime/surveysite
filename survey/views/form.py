from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.generic import View, TemplateView
from django.views.generic.base import ContextMixin
from hashlib import sha512
from itertools import repeat
import logging
from survey.forms import ResponseForm, get_anime_response_form, MissingAnimeForm
from survey.models import Anime, AnimeName, AnimeResponse, Response, MtmUserResponse
from survey.util import AnimeUtil
from .mixins import SurveyMixin, RequireSurveyOngoingMixin, UserMixin

@method_decorator([never_cache, login_required], name='dispatch')
class FormView(UserMixin, RequireSurveyOngoingMixin, SurveyMixin, ContextMixin, View):
    __username_hash = None
    __response_public_id = None

    def get(self, request, *args, **kwargs):
        try:
            previous_response, response_is_linked_to_user = self.__get_previous_response()
        except UserAlreadyRespondedException:
            messages.error(request, 'You already responded to this survey!')
            return redirect('survey:index')

        survey = self.get_survey()
        anime_list, _, _ = self.get_anime_lists()

        responseform = ResponseForm(
            instance=previous_response,
            initial={'link_user_to_response': response_is_linked_to_user}
        ) if previous_response else ResponseForm()
        animeresponseform_dict = {}

        # Get the anime response forms, bound to already stored anime responses whenever possible
        # (Saving what anime an AnimeResponseForm belongs to requires AnimeResponse.anime to be editable, so I just store it in the prefix)
        for anime in anime_list:
            AnimeResponseForm = get_anime_response_form(survey.is_preseason, AnimeUtil.anime_is_continuing(anime, survey))
            animeresponse_queryset = AnimeResponse.objects.filter(response=previous_response, anime=anime) if previous_response else None
            if animeresponse_queryset and animeresponse_queryset.count() == 1:
                animeresponseform_dict[anime.id] = AnimeResponseForm(prefix=str(anime.id), instance=animeresponse_queryset.first())
            else:
                animeresponseform_dict[anime.id] = AnimeResponseForm(prefix=str(anime.id))

        # Render the form
        if previous_response:
            messages.info(request, 'Loaded your previous response.')
        return self.__render_form(responseform, animeresponseform_dict)

    def post(self, request, *args, **kwargs):
        try:
            previous_response, _ = self.__get_previous_response()
        except UserAlreadyRespondedException:
            messages.error(request, 'You already responded to this survey!')
            return redirect('survey:index')

        username_hash = self.__get_username_hash()
        survey = self.get_survey()
        anime_list, _, _ = self.get_anime_lists()

        responseform = ResponseForm(request.POST, instance=previous_response) if previous_response else ResponseForm(request.POST)
        existing_animeresponseform_list = []
        new_animeresponseform_list = []

        # Get the anime response forms, bound to already stored anime responses whenever possible
        for anime in anime_list:
            AnimeResponseForm = get_anime_response_form(survey.is_preseason, AnimeUtil.anime_is_continuing(anime, survey))
            animeresponse_queryset = AnimeResponse.objects.filter(response=previous_response, anime=anime) if previous_response else None
            if animeresponse_queryset and animeresponse_queryset.count() == 1:
                existing_animeresponseform_list.append(AnimeResponseForm(request.POST, prefix=str(anime.id), instance=animeresponse_queryset.first()))
            else:
                new_animeresponseform_list.append(AnimeResponseForm(request.POST, prefix=str(anime.id)))

        # If all the forms contain valid data, save them
        if responseform.is_valid() and all(map(lambda animeresponseform: animeresponseform.is_valid(), existing_animeresponseform_list + new_animeresponseform_list)):
            response = responseform.save(commit=False)
            response.survey = survey
            response.save()

            # Get and update the previous AnimeResponse objects, or create new ones
            existing_animeresponse_list = []
            new_animeresponse_list = []
            for animeresponseform, is_existing in list(zip(existing_animeresponseform_list, repeat(True))) + list(zip(new_animeresponseform_list, repeat(False))):
                if not animeresponseform.is_empty() or is_existing:
                    animeresponse = animeresponseform.save(commit=False)
                    animeresponse.anime = Anime.objects.get(pk=int(animeresponseform.prefix))
                    animeresponse.response = response
                    if is_existing:
                        existing_animeresponse_list.append(animeresponse)
                    else:
                        new_animeresponse_list.append(animeresponse)

            # Update existing or create new AnimeResponse objects in the database
            AnimeResponse.objects.bulk_update(existing_animeresponse_list, ['watching', 'underwatched', 'score', 'expectations'])
            AnimeResponse.objects.bulk_create(new_animeresponse_list)

            # Store in a lookup table what survey the user has responded to, and if possible also which response this is
            link_user_to_response = responseform.cleaned_data['link_user_to_response']
            mtmuserresponse, _ = MtmUserResponse.objects.get_or_create(username_hash=username_hash, survey=survey)
            if link_user_to_response and not mtmuserresponse.response:
                mtmuserresponse.response = response
                mtmuserresponse.save()
            elif not link_user_to_response and mtmuserresponse.response:
                mtmuserresponse.response = None
                mtmuserresponse.save()

            messages.success(
                request,
                f'Successfully updated your response to {survey}!' if previous_response else f'Successfully filled in {survey}!'
            )

            # Redirect to index if the response is linked to the user, otherwise show a page with a link to edit the response
            if link_user_to_response:
                return redirect('survey:index')
            else:
                context = self.get_context_data()
                context['response_url'] = request.build_absolute_uri() + '?response=' + str(response.public_id)
                return render(request, 'survey/form_link.html', context)

        # If at least one form contains invalid data, re-render the form
        else:
            messages.error(request, 'One or more of your answers are invalid.')
            animeresponseform_dict = {int(form.prefix): form for form in existing_animeresponseform_list + new_animeresponseform_list}
            return self.__render_form(responseform, animeresponseform_dict)

    def __render_form(self, responseform, animeresponseform_dict):
        """Renders a survey form using the provided data."""
        survey = self.get_survey()

        def modify(anime):
            # Get anime names
            names = anime.animename_set.all()
            japanese_name = names.filter(anime_name_type=AnimeName.AnimeNameType.JAPANESE_NAME, official=True).first()
            anime.japanese_name = japanese_name if japanese_name else names.filter(anime_name_type=AnimeName.AnimeNameType.JAPANESE_NAME, official=False).first()
            english_name  = names.filter(anime_name_type=AnimeName.AnimeNameType.ENGLISH_NAME , official=True).first()
            anime.english_name  = english_name  if english_name  else names.filter(anime_name_type=AnimeName.AnimeNameType.ENGLISH_NAME , official=False).first()
            short_name    = names.filter(anime_name_type=AnimeName.AnimeNameType.SHORT_NAME   , official=True).first()
            anime.short_name    = short_name    if short_name    else names.filter(anime_name_type=AnimeName.AnimeNameType.SHORT_NAME   , official=False).first()

            # Get whether the anime is still ongoing or not
            anime.is_ongoing = survey.year != anime.start_year or survey.season != anime.start_season

            # Get a response form for the anime
            anime.animeresponseform = animeresponseform_dict[anime.id]

            return anime

        _, anime_series_list, special_anime_list = self.get_anime_lists()
        anime_series_list = map(modify, anime_series_list)
        special_anime_list = map(modify, special_anime_list)

        context = self.get_context_data()
        context['anime_series_list'] = anime_series_list
        context['special_anime_list'] = special_anime_list
        context['responseform'] = responseform
        if self.__response_public_id:
            context['response_public_id'] = self.__response_public_id

        return render(self.request, 'survey/form.html', context)

    def __get_previous_response(self):
        """Returns the previous response if the user submitted one or None, and whether the user linked their response to their account.
        Raises UserAlreadyRespondedException if the user already responded but does not have a response linked to their account."""

        previous_response_lookup, user_responded = self.__get_previous_response_from_lookup_table()
        previous_response_getpost = self.__get_previous_response_from_getpost_parameter()

        # Check whether the user responded but does not have a response linked
        if user_responded and not previous_response_lookup and not previous_response_getpost:
            raise UserAlreadyRespondedException()

        if previous_response_getpost:
            self.__response_public_id = previous_response_getpost.public_id

        # Check whether a lookup response and a get-param response were found that are different,
        # this should be impossible because a user is not allowed to answer the same survey twice
        # and because __get_previous_response_from_getpost_parameter() checks if the get-param response belongs to this survey and user
        if previous_response_lookup and previous_response_getpost and previous_response_getpost != previous_response_lookup:
            messages.warning(self.request, f'Cannot load your response with ID "{previous_response_getpost.public_id}" as your account already has a linked response!')
            logging.error(f'Tried to load two different responses ({previous_response_lookup.id}, {previous_response_getpost.id}), which should not be possible.')
            return previous_response_lookup, True

        return previous_response_lookup or previous_response_getpost, bool(previous_response_lookup)

    def __get_previous_response_from_lookup_table(self):
        """Tries to get the user's previous Response from MtmUserResponse.
        Returns the Response (or None if not found) and a boolean indicating whether the user answered the survey."""

        username_hash = self.__get_username_hash()
        survey = self.get_survey()
        mtmuserresponse_queryset = MtmUserResponse.objects.filter(username_hash=username_hash, survey=survey)

        # No need to check whether there are multiple entries in the queryset as there's a uniqueness constraint on username_hash and survey
        if not mtmuserresponse_queryset.exists():
            return None, False
        else:
            response = mtmuserresponse_queryset.first().response
            return response, True

    def __get_previous_response_from_getpost_parameter(self):
        """Checks whether the user has a response's public ID set as a GET or POST parameter and returns the Response if possible."""

        if self.request.method == 'GET':
            response_public_id = self.request.GET.get('response', default=None)
        elif self.request.method == 'POST':
            response_public_id = self.request.POST.get('response-id', default=None)
        else:
            response_public_id = None

        if not response_public_id:
            return None

        response_queryset = Response.objects.filter(public_id=response_public_id)
        response_queryset_count = len(response_queryset)
        if response_queryset_count == 0:
            messages.warning(self.request, f'Unable to find your response with ID "{response_public_id}"!')
            return None
        if response_queryset_count > 1:
            messages.warning(self.request, f'An error occurred while retrieving your response with ID "{response_public_id}".')
            logging.error(f'Multiple responses with public ID "{response_public_id}" found!')
            return None
        response = response_queryset.first()

        # Handle some funny edge-cases here

        # Check whether the response belongs to another survey
        if response.survey != self.get_survey():
            messages.warning(self.request, f'Your response with ID "{response_public_id}" belongs to {response.survey}!')
            return None

        # Check whether the response belongs to someone else (to our knowledge)
        mtmuserresponse_queryset = MtmUserResponse.objects.filter(response=response)
        mtmuserresponse_queryset_count = len(mtmuserresponse_queryset)
        if mtmuserresponse_queryset_count > 1:
            logging.error(f'A user tried to load a response with public ID "{response.public_id}" but multiple MtmUserResponse entries were found for this response!')
        if mtmuserresponse_queryset_count and mtmuserresponse_queryset.first().username_hash != self.__get_username_hash():
            messages.warning(self.request, f'Cannot load the response with ID "{response.public_id}" as that response belongs to someone else!')
            return None

        return response

    def __get_username_hash(self):
        """Returns a SHA-512 has of the username of a user (should be a lowercase version of their Reddit username)."""
        if not self.__username_hash:
            user = self.request.user
            self.__username_hash = sha512(user.username.encode('utf-8')).digest()
        return self.__username_hash



class UserAlreadyRespondedException(Exception):
    """Exception used to indicate a user already responded to a survey without having linked their account to a response."""
    pass



@method_decorator([login_required], name='dispatch')
class MissingAnimeView(RequireSurveyOngoingMixin, SurveyMixin, TemplateView):
    template_name = 'survey/form_missinganime.html'

    def get(self, request, *args, **kwargs):
        self.extra_context = {
            'form': MissingAnimeForm()
        }
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        form = MissingAnimeForm(request.POST)
        if form.is_valid():
            missinganime = form.save(commit=False)
            missinganime.survey = self.get_survey()
            missinganime.user = request.user
            missinganime.save()

            form = MissingAnimeForm()
            messages.success(request, 'Successfully sent missing anime! Your request will be manually reviewed.')
        else:
            messages.error(request, 'Something went wrong.')

        self.extra_context = {
            'form': form
        }
        return super().get(request, *args, **kwargs)
