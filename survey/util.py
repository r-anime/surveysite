from django.db.models import Q, F
from django.shortcuts import get_object_or_404
from django.http import Http404
from .models import Anime, Survey


class AnimeUtil:
    anime_series_filter = Q(anime_type=Anime.AnimeType.TV_SERIES) | Q(anime_type=Anime.AnimeType.ONA_SERIES) | Q(anime_type=Anime.AnimeType.BULK_RELEASE)
    special_anime_filter = ~anime_series_filter

    @staticmethod
    def combine_year_season(year, season):
        return year * 10 + season

    @staticmethod
    def is_ongoing_filter_func(current_year_season):
        return Q(start_year_season__lte=current_year_season) & ( \
            AnimeUtil.anime_series_filter  & (Q(end_year_season__gte   =current_year_season) | Q(end_year_season   =None)) | \
            AnimeUtil.special_anime_filter & (Q(subbed_year_season__gte=current_year_season) | Q(subbed_year_season=None))
        )

    @staticmethod
    def annotate_year_season(queryset):
        return queryset.annotate(
            start_year_season  = AnimeUtil.combine_year_season(F('start_year') , F('start_season') ),
            end_year_season    = AnimeUtil.combine_year_season(F('end_year')   , F('end_season')   ),
            subbed_year_season = AnimeUtil.combine_year_season(F('subbed_year'), F('subbed_season')),
        )

    @staticmethod
    def anime_is_series(anime):
        return anime.anime_type == Anime.AnimeType.TV_SERIES or anime.anime_type == Anime.AnimeType.ONA_SERIES or anime.anime_type == Anime.AnimeType.BULK_RELEASE
    
    @staticmethod
    def increment_year_season(year_season):
        result = year_season + 1
        if result % 10 == 4:
            result = result + 10 - 4
        return result


class SurveyUtil:
    @staticmethod
    def get_survey_or_404(year, season, pre_or_post):
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


# Returns None if not authenticated
def get_username(user):
    if not user.is_authenticated: return None

    if len(user.socialaccount_set.all()) > 0:
        return user.socialaccount_set.all()[0].uid
    else:
        return user.username