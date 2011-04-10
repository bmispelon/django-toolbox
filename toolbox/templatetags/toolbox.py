from django import template
from django.template.defaultfilters import floatformat as floatformat_

register = template.Library()

@register.filter
def lookup(dict, key):
    try:
        return dict.get(key)
    except AttributeError:
        return None

@register.simple_tag
def percent(sample, total, floatformat=-2):
    """Prints out the percentage of `sample` with regard to `total`.
    The output is passed through django's floatformat template filter
    and can be controlled using the floatformat parameter."""
    f = 100. * sample / total
    return floatformat_(f, floatformat)
