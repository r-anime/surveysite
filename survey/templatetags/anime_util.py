from django import template
from django.conf import settings
from ..models import Anime, AnimeName
from ..util import AnimeUtil

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
def get_anime_image_url(anime, variant='l', default=''):
    if anime.image_set.count():
        anime_image = anime.image_set.first()
        if variant == 's':
            image_file = anime_image.file_small
        elif variant == 'm':
            image_file = anime_image.file_medium
        else:
            image_file = anime_image.file_large

        image_url = image_file.url
    else:
        image_url = None

    if not default:
        default = settings.STATIC_URL + ('/' if not settings.STATIC_URL.endswith('/') else '') + 'survey/image-unavailable.png'
    return image_url if image_url else default

@register.simple_tag
def get_season_name(season_idx, start_with_capital=True):
    season_name = Anime.AnimeSeason(season_idx).name
    if start_with_capital:
        return season_name[0] + season_name[1:].lower()
    else:
        return season_name.lower()

@register.inclusion_tag('survey/anime_names.html')
def get_official_names(anime, tag=None):
    return {
        'anime_name_list': AnimeUtil.get_name_list(anime),
        'tag': tag,
    }