from django import template
from django.template.defaultfilters import floatformat as floatformat_
from django.utils.encoding import smart_unicode

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

@register.filter
def intspace(i, spacer='\xc2\xa0'): # Non-breaking space
    """Similar to django's intcomma but one can specify the character used to
    separate the groups of digits (a non-breaking space is used by default).
    """
    spacer = smart_unicode(spacer)
    
    try:
        i = int(i)
    except ValueError:
        return u''
    
    acc = []
    while i:
        remainder, i = i % 1000, i / 1000
        format = i and '%03i' or '%i'
        acc.append(format % remainder)
    return spacer.join(reversed(acc))
