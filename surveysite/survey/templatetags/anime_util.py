from django import template

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