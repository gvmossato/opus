from django import template

register = template.Library()

@register.simple_tag
def update_with(value):
    return value
