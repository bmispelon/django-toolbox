"""
A collection of template filters to cutomize form elements inside templates.
It's basically a drop-in replacement for b-utils, except it has some backward
incompatibility issues with it, so it was turned into an independent module.
"""

from django import template
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

register = template.Library()

FIELDWRAPPER_TPL = u"""
<div class="%(wrapper_class)s">
    %(errors)s
    %(label)s%(break)s
    %(field)s
    %(helptext)s
</div>"""

DEFAULT_WRAPPER_CLASS = 'fieldWrapper'

WRAP_BREAK = 1
WRAP_NOBREAK = 2

_USE_FIELD_LABEL = object()


class BField(object):
    def __init__(self, field, wrap=None, label=None, klass=None, helptext=None):
        self.field = field
        self.wrap = wrap
        self.label = label
        self.klass = klass
        self.helptext = helptext
    
    @classmethod
    def factory(cls, field, **kwargs):
        if isinstance(field, cls):
            for k, v in kwargs.items():
                setattr(field, k, v)
            return field
        else:
            return cls(field, **kwargs)
    
    def __unicode__(self):
        try:
            return self.render()
        except AttributeError:
            return u''
    
    def render(self):
        """Render the node as HTML"""
        if self.wrap is None:
            if self.label is None:
                if self.helptext is None:
                    return self.render_field()
                else: # self.helptext is not None
                    return self.render_helptext()
            else: # self.label is not None
                return self.render_label()
        else: # self.wrap is not None
            return self.render_wrap()
    
    def render_wrap(self):
        return mark_safe(FIELDWRAPPER_TPL % {
            'errors': self.field.errors,
            'label': self.render_label(),
            'break': self.wrap == WRAP_BREAK and u'<br />' or u'',
            'field': self.render_field(),
            'helptext': self.render_helptext(),
            'wrapper_class': DEFAULT_WRAPPER_CLASS,
        })
    
    def render_label(self):
        """Render a label tag corresponding to the field with a custom text.
        The self.klass parameter is not taken into account."""
        label = self.field.label if self.label is _USE_FIELD_LABEL else self.label
        attrs = self.field.errors and {'class': 'hasError'} or None
        return self.field.label_tag(contents=label, attrs=attrs)
    
    def render_field(self):
        """Render the form field, with a custom css class added."""
        if self.klass is not None:
            attrs = {'class': self.klass}
        else:
            attrs = {}
        return self.field.as_widget(attrs=attrs)
    
    def render_helptext(self):
        helptext = self.helptext is None and self.field.help_text or self.helptext
        if helptext:
            return u'<span class="helptext">%s</span>' % helptext
        else:
            return u''


@register.filter
def blabel(field, label=_USE_FIELD_LABEL):
    return BField.factory(field, label=label)

@register.filter
def bwrap(field, break_after_label=False):
    if break_after_label:
        wrap = WRAP_BREAK
    else:
        wrap = WRAP_NOBREAK
    return BField.factory(field, wrap=wrap)

@register.filter
def bclass(field, klass=None):
    return BField.factory(field, klass=klass)

@register.filter
def bhelptext(field, helptext=None):
    return BField.factory(field, helptext=helptext)

@register.filter
def bform(form):
    try:
        wrapped_fields = [bwrap(field) for field in form]
    except TypeError:
        return u""
    return mark_safe('\n'.join(wrap.render() for wrap in wrapped_fields))

def split_fields(fields):
    """Normalize the given argument to return a list of field names.
    The supported formats are:
        * A list of str (return unchanged)
        * A string of comma-separated fields
        * A string of whitespace-separated fields
    """
    if isinstance(fields, basestring):
        fields = fields.replace(',', ' ').split()
    return fields

@register.filter
def bfilter(form, fields):
    """Return only the given fields from the given form (as a list)."""
    return [form[f] for f in split_fields(fields)]

@register.filter
def bexclude(form, excluded):
    """Return a list of all the fields in the given form, except those excluded."""
    excluded = set(split_fields(excluded))
    return [form[f] for f in form.fields if f not in excluded]
