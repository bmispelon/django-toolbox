from django import template
from django.template.defaultfilters import floatformat as floatformat_
try: # django < 1.4
    from django.template.defaultfilters import slice_ as slice_filter
except ImportError: # django 1.4
    from django.template.defaultfilters import slice_filter
from django.utils.encoding import smart_unicode
from django.utils.safestring import mark_safe
from itertools import izip

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
    except (ValueError, TypeError):
        return u''
    
    acc = []
    while i:
        remainder, i = i % 1000, i / 1000
        format = i and '%03i' or '%i'
        acc.append(format % remainder)
    return spacer.join(reversed(acc))


@register.filter
def multifield_list(boundfield, idx=None):
    # XXX
    rendered = str(boundfield)
    widgets = [mark_safe(w) for w in rendered.split('\n')]
    
    if idx is None:
        return widgets
    else:
        try:
            return widgets[int(idx)]
        except IndexError:
            return u''


@register.filter
def firstline(txt):
    """Return the first line of a text."""
    return txt.split('\n')[0]


@register.filter
def slicelines(txt, arg):
    """Like django's slice template tag but converts the (text) argument
    to a list of lines first."""
    return '\n'.join(slice_filter(txt.split('\n'), arg))


class ZipChain(object):
    """Allow chaining several calls to the zip filter."""
    def __init__(self, *iterables):
        self.iterables = iterables
    
    def add_iterables(self, *iterables):
        self.iterables.extend(iterable)
    
    @classmethod
    def factory(cls, var, *iterables):
        if isinstance(var, cls):
            var.add_iterables(*iterables)
            return var
        else:
            return cls(var, *iterables)
    
    def __iter__(self):
        return izip(*self.iterables)


@register.filter('zip')
def zip_(a, b):
    """Zips two iterable together. Useful with forloops for example.
    Usage: {% for foo, bar in foos|zip:bars %}
    Can be chained to zip more than two iterables:
    {% for foo, bar, baz in foos|zip:bars|zip:bazes %}
    
    """
    return ZipChain.factory(a, b)


@register.filter
def sortby(sequence, sort_key=None):
    if sort_key is None:
        return sorted(sequence)

    def sort_function(item):
        return getattr(item, sort_key)

    return sorted(sequence, key=sort_function)
