from datetime import datetime
from django.db.models import Q
from random import randint
from survey.models import Anime, Survey
from survey.util.anime import anime_series_filter, annotate_year_season, calc_season_difference, combine_year_season, is_ongoing_filter_func, special_anime_filter
from typing import Optional, Union


def try_get_survey(year: int, season: Anime.AnimeSeason, pre_or_post: str) -> Union[Survey, None]:
    """Tries to get the specified survey, returns None if not found."""
    if pre_or_post == 'pre':
        is_preseason = True
    elif pre_or_post == 'post':
        is_preseason = False
    else:
        return None

    try:
        survey: Survey = Survey.objects.get(year=year, season=season, is_preseason=is_preseason)
    except (Survey.DoesNotExist, Survey.MultipleObjectsReturned):
        return None

    return survey


def get_survey_anime(survey: Survey):
    """Gets the anime that should be included in the given survey.

    Parameters
    ----------
    survey : Survey
        The survey for which you want to get the anime.

    Returns
    -------
    (QuerySet, QuerySet, QuerySet)
        Querysets of respectively all the anime, only anime series, and only special anime that should be included in this survey.
    """
    current_year_season = combine_year_season(survey.year, survey.season)

    anime_queryset = annotate_year_season(
        Anime.objects
    ).filter(
        is_ongoing_filter_func(current_year_season)
    )


    survey_anime_series_filter = anime_series_filter
    survey_special_anime_filter = special_anime_filter

    # Special anime in pre-season surveys have to start in the survey's season and in post-season surveys have to end in that season,
    # because I cba to track when/whether individual parts of irregularly-released stuff releases
    if survey.is_preseason:
        survey_special_anime_filter = survey_special_anime_filter & Q(start_year_season=current_year_season)
    else:
        survey_special_anime_filter = survey_special_anime_filter & Q(subbed_year_season=current_year_season)
    
    
    anime_series_queryset = anime_queryset.filter(
        survey_anime_series_filter
    )
    special_anime_queryset = anime_queryset.filter(
        survey_special_anime_filter
    )
    combined_anime_queryset = anime_queryset.filter(
        survey_anime_series_filter | survey_special_anime_filter
    )
    return combined_anime_queryset, anime_series_queryset, special_anime_queryset


def get_old_survey_cache_timeout() -> Optional[int]:
    return None


def is_survey_old(survey: Survey) -> bool:
    """Get whether a survey is considered old and thus should have variables related to it cached for longer."""
    survey_yearseason = combine_year_season(survey.year, survey.season)
    current_yearseason = combine_year_season(datetime.now().year, datetime.now().month // 4)
    return calc_season_difference(current_yearseason, survey_yearseason) >= 2


def get_survey_cache_timeout(survey: Survey) -> Optional[int]:
    """Get for how long values belonging to the given survey have to be cached."""
    # If survey from two or more seasons ago, never let cache expire, otherwise between 6 and 10 hours
    if is_survey_old(survey):
        return get_old_survey_cache_timeout()
    else:
        return 60*60*8 + randint(-60*60*2, 60*60*2)
