from django import template

register = template.Library()

@register.filter
def listify(value):
    return list(value)
