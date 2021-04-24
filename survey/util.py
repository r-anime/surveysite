from django.db.models import Q, F
from django.shortcuts import get_object_or_404
from django.http import Http404
from .models import Anime, Survey, AnimeName
from datetime import datetime
from random import randint
from django.conf import settings


class AnimeUtil:
    """Class with various static utility methods related to Anime objects."""

    anime_series_filter = Q(anime_type=Anime.AnimeType.TV_SERIES) | Q(anime_type=Anime.AnimeType.ONA_SERIES) | Q(anime_type=Anime.AnimeType.BULK_RELEASE)
    special_anime_filter = ~anime_series_filter

    @staticmethod
    def combine_year_season(year, season):
        """Combines a year and a season into a single value."""
        return year * 10 + season

    @staticmethod
    def is_ongoing_filter_func(current_year_season):
        """Generates a queryset filter that only filters ongoing anime."""
        return Q(start_year_season__lte=current_year_season) & ( \
            AnimeUtil.anime_series_filter  & (Q(end_year_season__gte   =current_year_season) | Q(end_year_season   =None)) | \
            AnimeUtil.special_anime_filter & (Q(subbed_year_season__gte=current_year_season) | Q(subbed_year_season=None))
        )

    @staticmethod
    def annotate_year_season(queryset):
        """Annotates an anime queryset with their year-season value (i.e. year and season combined into one value)."""
        return queryset.annotate(
            start_year_season  = AnimeUtil.combine_year_season(F('start_year') , F('start_season') ),
            end_year_season    = AnimeUtil.combine_year_season(F('end_year')   , F('end_season')   ),
            subbed_year_season = AnimeUtil.combine_year_season(F('subbed_year'), F('subbed_season')),
        )

    @staticmethod
    def anime_is_series(anime):
        """Checks whether an anime is a series or a special anime."""
        return anime.anime_type == Anime.AnimeType.TV_SERIES or anime.anime_type == Anime.AnimeType.ONA_SERIES or anime.anime_type == Anime.AnimeType.BULK_RELEASE
    
    @staticmethod
    def increment_year_season(year_season):
        """Moves the given year-season value one season forward."""
        result = year_season + 1
        if result % 10 == 4:
            result = result + 10 - 4
        return result

    @staticmethod
    def calc_season_difference(year_season_a, year_season_b):
        """Calculate how many seasons there are between two year-season values (a-b)."""
        def convert(year_season):
            season = year_season % 10
            return year_season + season * 1.5

        diff = convert(year_season_a) - convert(year_season_b)
        return diff * 4 / 10

    @staticmethod
    def get_name_list(anime, official_names_only=True):
        animename_queryset = anime.animename_set.filter(official=official_names_only)
        japanese_names = animename_queryset.filter(anime_name_type=AnimeName.AnimeNameType.JAPANESE_NAME)
        english_names = animename_queryset.filter(anime_name_type=AnimeName.AnimeNameType.ENGLISH_NAME)
        short_names = animename_queryset.filter(anime_name_type=AnimeName.AnimeNameType.SHORT_NAME)

        animename_list = list(japanese_names) + list(english_names) + list(short_names)
        return [animename.name for animename in animename_list]

    @staticmethod
    def get_image_url_list(anime, default=''):
        image_set = anime.image_set.all()
        image_list = []
        if len(image_set):
            image_list = map(
                lambda image: {
                    'urls': {
                        's': image.file_small.url,
                        'm': image.file_medium.url,
                        'l': image.file_large.url,
                    },
                    'alt': image.name,
                },
                image_set
            )
            return list(image_list)
        else:
            if not default:
                default = settings.STATIC_URL + ('/' if not settings.STATIC_URL.endswith('/') else '') + 'survey/img/image-unavailable.png'
            return [{
                'urls': {
                    's': default,
                    'm': default,
                    'l': default,
                },
                'alt': 'Image unavailable',
            }]

    @staticmethod
    def anime_is_continuing(anime, survey):
        """Gets whether the anime is a continuing anime (for pre-season surveys, start year/season != survey year/season) or not."""
        return survey.year != anime.start_year or survey.season != anime.start_season


class SurveyUtil:
    """Class with various static utility methods related to Survey objects."""

    @staticmethod
    def get_survey_or_404(year, season, pre_or_post):
        """Tries to get the specified survey or raises an Http404 exception."""
        if pre_or_post == 'pre':
            is_preseason = True
        elif pre_or_post == 'post':
            is_preseason = False
        else:
            raise Http404("Survey does not exist!")

        survey = get_object_or_404(Survey, year=year, season=season, is_preseason=is_preseason)
        return survey

    @staticmethod
    def get_survey_anime(survey):
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
        current_year_season = AnimeUtil.combine_year_season(survey.year, survey.season)

        anime_queryset = AnimeUtil.annotate_year_season(
            Anime.objects
        ).filter(
            AnimeUtil.is_ongoing_filter_func(current_year_season)
        )


        anime_series_filter = AnimeUtil.anime_series_filter
        special_anime_filter = AnimeUtil.special_anime_filter

        # Special anime in pre-season surveys have to start in the survey's season and in post-season surveys have to end in that season,
        # because I cba to track when/whether individual parts of irregularly-released stuff releases
        if survey.is_preseason:
            special_anime_filter = special_anime_filter & Q(start_year_season=current_year_season)
        else:
            special_anime_filter = special_anime_filter & Q(subbed_year_season=current_year_season)
        
        
        anime_series_queryset = anime_queryset.filter(
            anime_series_filter
        )
        special_anime_queryset = anime_queryset.filter(
            special_anime_filter
        )
        combined_anime_queryset = anime_queryset.filter(
            anime_series_filter | special_anime_filter
        )
        return combined_anime_queryset, anime_series_queryset, special_anime_queryset

    @staticmethod
    def get_old_survey_cache_timeout():
        return None

    @staticmethod
    def is_survey_old(survey):
        """Get whether a survey is considered old and thus should have variables related to it cached for longer."""
        survey_yearseason = AnimeUtil.combine_year_season(survey.year, survey.season)
        current_yearseason = AnimeUtil.combine_year_season(datetime.now().year, datetime.now().month // 4)
        return AnimeUtil.calc_season_difference(current_yearseason, survey_yearseason) >= 2

    @staticmethod
    def get_survey_cache_timeout(survey):
        """Get for how long values belonging to the given survey have to be cached."""
        # If survey from two or more seasons ago, never let cache expire, otherwise between 6 and 10 hours
        if SurveyUtil.is_survey_old(survey):
            return SurveyUtil.get_old_survey_cache_timeout()
        else:
            return 60*60*8 + randint(-60*60*2, 60*60*2)


# Returns None if not authenticated
def get_user_info(user):
    """Gets displayable informatin about the user. Returns None if the user is not authenticated."""
    if not user.is_authenticated: return None

    socialaccount_queryset = user.socialaccount_set.all()
    reddit_account_queryset = socialaccount_queryset.filter(provider='reddit')
    if len(reddit_account_queryset) == 1:
        account = reddit_account_queryset[0]
        username = account.uid
        image = account.extra_data['icon_img']
    elif len(socialaccount_queryset) > 1:
        account = user.socialaccount_set.all()[0]
        username = account.uid
        image = None
    else:
        username = user.username
        image = None

    return {
        'username': username,
        'image': image,
    }