from django import template

register = template.Library()

@register.inclusion_tag('survey/form_card.html')
def create_form_card(anime, is_preseason, is_series):
    return {
        'anime': anime,
        'is_preseason': is_preseason,
        'is_series': is_series,
    }