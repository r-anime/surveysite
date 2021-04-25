from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.decorators.cache import never_cache
from itertools import repeat
import logging
from survey.forms import ResponseForm, get_anime_response_form
from survey.models import Anime, AnimeName, AnimeResponse, Response
from survey.util import AnimeUtil, SurveyUtil, get_user_info

@login_required
@never_cache
def form(request, year, season, pre_or_post):
    """Generates the form view, where users can respond to a survey. Requires the user being logged in."""

    # Send the user back to the index if the survey is closed
    survey = SurveyUtil.get_survey_or_404(year, season, pre_or_post)
    if not survey.is_ongoing:
        messages.error(request, str(survey) + ' is closed!')
        return redirect('survey:index')

    anime_list, anime_series_list, special_anime_list = SurveyUtil.get_survey_anime(survey)

    # Load the previous response if possible
    response_session_key = 'survey_%i_response' % survey.id
    if response_session_key in request.session:
        response_public_id = request.session[response_session_key]
        try:
            previous_response = Response.objects.get(public_id=response_public_id)
        except Response.DoesNotExist:
            messages.warning(request, 'Response with ID "%s" does not exist!' % response_public_id)
            previous_response = None
        except Response.MultipleObjectsReturned:
            messages.warning(request, 'Unable to load response with ID "%s".' % response_public_id)
            logging.error('Multiple responses with public ID "%s" found!' % response_public_id)
            previous_response = None
    else:
        previous_response = None


    # -----
    # The user has submitted a response
    # -----
    if request.method == 'POST':
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

            AnimeResponse.objects.bulk_update(existing_animeresponse_list, ['watching', 'underwatched', 'score', 'expectations'])
            AnimeResponse.objects.bulk_create(new_animeresponse_list)

            if previous_response:
                messages.success(request, 'Successfully updated your response to %s!' % str(survey))
            else:
                messages.success(request, 'Successfully filled in %s!' % str(survey))

            request.session['survey_%i_response' % survey.id] = response.public_id.hex
            return redirect('survey:index')

        # If at least one form contains invalid data, re-render the form
        else:
            messages.error(request, 'One or more of your answers are invalid.')
            animeresponseform_dict = {int(form.prefix): form for form in existing_animeresponseform_list + new_animeresponseform_list}
            return __render_form(request, survey, anime_series_list, special_anime_list, responseform, animeresponseform_dict)


    # -----
    # The user wants to view the form
    # -----
    elif request.method == 'GET':
        responseform = ResponseForm(instance=previous_response) if previous_response else ResponseForm()
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
        return __render_form(request, survey, anime_series_list, special_anime_list, responseform, animeresponseform_dict)



def __render_form(request, survey, anime_series_list, special_anime_list, responseform, animeresponseform_dict):
    """Renders a survey form using the provided data."""
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

    anime_series_list = map(modify, anime_series_list)
    special_anime_list = map(modify, special_anime_list)

    context = {
        'survey': survey,
        'anime_series_list': anime_series_list,
        'special_anime_list': special_anime_list,
        'user_info': get_user_info(request.user),
        'responseform': responseform,
    }
    return render(request, 'survey/form.html', context)