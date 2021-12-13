from django import template


def update_with(value):
    return value


register = template.Library()
register.filter('update_with', update_with)
