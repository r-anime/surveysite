from django import template
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
    return AnimeUtil.get_anime_image_url(anime, variant=variant, default=default)

@register.inclusion_tag('survey/anime_image_carousel.html')
def get_anime_image_carousel(anime, variant='l', enable_controls=True):
    image_set = anime.image_set.all()

    def get_data(image):
        image_file = image.file_small if variant == 's' else image.file_medium if variant == 'm' else image.file_large
        return {
            'url': image_file.url,
            'alt': image.name,
            'width': image_file.width,
            'height': image_file.height,
        }

    image_list = list(map(get_data, image_set))
    max_width  = max([image['width' ] for image in image_list]) if image_list else None
    max_height = max([image['height'] for image in image_list]) if image_list else None

    return {
        'image_list': image_list,
        'id': anime.id,
        'width': max_width,
        'height': max_height,
        'enable_controls': enable_controls,
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
    return {
        'anime_name_list': AnimeUtil.get_name_list(anime),
        'tag': tag,
    }