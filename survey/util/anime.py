from django.conf import settings
from django.db.models import Q, F
from django.db.models.manager import BaseManager
from django.db.models.query import QuerySet
from survey.models import Anime, AnimeName, Image, Survey
from survey.util.data import ImageViewModel
from typing import NewType, Optional, TypeVar, Union

TAnimeQuerySet = TypeVar('TAnimeQuerySet', bound=QuerySet[Anime])
YearSeason = NewType('YearSeason', int)

anime_series_filter = Q(anime_type=Anime.AnimeType.TV_SERIES) | Q(anime_type=Anime.AnimeType.ONA_SERIES) | Q(anime_type=Anime.AnimeType.BULK_RELEASE)
special_anime_filter = ~anime_series_filter


def combine_year_season(year: int, season: Union[Anime.AnimeSeason, int]) -> YearSeason:
    """Combines a year and a season into a single value."""
    return YearSeason(year * 10 + season)


def is_ongoing_filter_func(current_year_season: YearSeason) -> Q:
    """Generates a queryset filter that only filters ongoing anime."""
    return Q(start_year_season__lte=current_year_season) & ( \
        anime_series_filter  & (Q(end_year_season__gte   =current_year_season) | Q(end_year_season   =None)) | \
        special_anime_filter & (Q(subbed_year_season__gte=current_year_season) | Q(subbed_year_season=None))
    )


def annotate_year_season(queryset: TAnimeQuerySet) -> TAnimeQuerySet:
    """Annotates an anime queryset with their year-season value (i.e. year and season combined into one value)."""
    return queryset.annotate(
        start_year_season  = combine_year_season(F('start_year') , F('start_season') ),
        end_year_season    = combine_year_season(F('end_year')   , F('end_season')   ),
        subbed_year_season = combine_year_season(F('subbed_year'), F('subbed_season')),
    )


def anime_is_series(anime: Anime) -> bool:
    """Checks whether an anime is a series or a special anime."""
    return anime.anime_type == Anime.AnimeType.TV_SERIES or anime.anime_type == Anime.AnimeType.ONA_SERIES or anime.anime_type == Anime.AnimeType.BULK_RELEASE


def increment_year_season(year_season: YearSeason) -> YearSeason:
    """Moves the given year-season value one season forward."""
    result = year_season + 1
    if result % 10 == 4:
        result = result + 10 - 4
    return YearSeason(result)


def calc_season_difference(year_season_a: YearSeason, year_season_b: YearSeason) -> int:
    """Calculate how many seasons there are between two year-season values (a-b)."""
    def convert(year_season: YearSeason) -> int:
        season = year_season % 10
        return year_season * 10 + season * 25

    diff = convert(year_season_a) - convert(year_season_b)
    return diff * 4 // 100


def get_name_list(anime: Anime, official_names_only: bool = True) -> list[str]:
    animename_queryset: BaseManager[AnimeName] = anime.animename_set.filter(official=official_names_only)
    japanese_names = animename_queryset.filter(anime_name_type=AnimeName.AnimeNameType.JAPANESE_NAME)
    english_names = animename_queryset.filter(anime_name_type=AnimeName.AnimeNameType.ENGLISH_NAME)
    short_names = animename_queryset.filter(anime_name_type=AnimeName.AnimeNameType.SHORT_NAME)

    animename_list = list(japanese_names) + list(english_names) + list(short_names)
    return [animename.name for animename in animename_list]


def get_image_url_list(anime: Anime, default: Optional[str] = None) -> list[ImageViewModel]:
    image_set: BaseManager[Image] = anime.image_set.all()
    imagedata_list = []
    if len(image_set):
        imagedata_list = map(
            lambda image: ImageViewModel(
                image.name,
                image.file_small.url,
                image.file_medium.url,
                image.file_large.url
            ),
            image_set
        )
        return list(imagedata_list)
    else:
        if not default:
            default = settings.STATIC_URL + ('/' if not settings.STATIC_URL.endswith('/') else '') + 'survey/img/image-unavailable.png'
        return [ImageViewModel(
            'Image unavailable',
            default,
            default,
            default
        )]


def anime_is_continuing(anime: Anime, survey: Survey) -> bool:
    """Gets whether the anime is a continuing anime (for pre-season surveys, start year/season != survey year/season) or not."""
    return survey.year != anime.start_year or survey.season != anime.start_season
