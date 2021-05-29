from django import template
from ..models import Anime, AnimeName
from ..util import AnimeUtil

register = template.Library()

@register.inclusion_tag('survey/anime_images.html')
def render_anime_images(anime, variant='l', enable_controls=True):
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
