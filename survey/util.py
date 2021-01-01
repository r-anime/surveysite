from django.db.models import Q, F
from .models import Anime


class AnimeUtil():
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
