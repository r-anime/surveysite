from django import template
from ..models import Anime, AnimeName

register = template.Library()

@register.inclusion_tag('survey/anime_image.html')
def get_anime_image(anime, css_class='', variant='l'):
    if anime.image_set.count():
        anime_image = anime.image_set.first()
        if variant == 's':
            image_file = anime_image.file_small
        elif variant == 'm':
            image_file = anime_image.file_medium
        else:
            image_file = anime_image.file_large
        
        image_url = image_file.url
        image_alt = anime_image.name
    else:
        image_url = None
        image_alt = None
    
    return {
        'image_url': image_url,
        'image_alt': image_alt,
        'css_class': css_class,
    }

@register.simple_tag
def get_season_name(season_idx, start_with_capital=True):
    season_name = Anime.AnimeSeason(season_idx).name
    if start_with_capital:
        return season_name[0] + season_name[1:].lower()
    else:
        return season_name.lower()

@register.inclusion_tag('survey/anime_names.html')
def get_official_names(anime, tag=None):
    name_queryset = anime.animename_set.filter(official=True)
    japanese_names = name_queryset.filter(anime_name_type=AnimeName.AnimeNameType.JAPANESE_NAME)
    english_names = name_queryset.filter(anime_name_type=AnimeName.AnimeNameType.ENGLISH_NAME)
    short_names = name_queryset.filter(anime_name_type=AnimeName.AnimeNameType.SHORT_NAME)

    anime_name_list = list(japanese_names) + list(english_names) + list(short_names)
    return {
        'anime_name_list': [name.name for name in anime_name_list],
        'tag': tag,
    }
