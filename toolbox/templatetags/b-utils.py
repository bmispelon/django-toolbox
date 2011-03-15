"""
A collection of template filters to cutomize form elements inside templates.
"""

from django import template
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

register = template.Library()

FIELDWRAPPER_TPL = u"""
<div class="fieldWrapper">
    %(errors)s
    %(label)s :%(break)s
    %(field)s
</div>"""


class BLabeledField(object):
    """A small class that allows chaining the different filters."""
    def __init__(self, field, label=None):
        self.field, self.label = field, label
    
    def __unicode__(self):
        field = self.field
        label = self.label
        
        if label is not None:
            label = conditional_escape(label)
        
        if isinstance(field, BWrappedField):
            bw = field
            return field.render(bw.field, label=label, br=bw.br)
        
        return self.render(self.field, label)
    
    def render(self, field, label=None):
        attrs = self.field.errors and {'class': 'hasError'} or None
        return self.field.label_tag(contents=self.label, attrs=attrs)


class BWrappedField(object):
    """A small class that allows chaining the different filters."""
    def __init__(self, field, br=False):
        self.field, self.br = field, br
    
    def __unicode__(self):
        field = self.field
        br = self.br
        
        if isinstance(field, BLabeledField):
            label = field.label
            field = field.field
        else:
            label = None
        
        return self.render(field, label=label, br=br)
    
    def render(self, field, label=None, br=False):
        return mark_safe(FIELDWRAPPER_TPL % {
            'errors': field.errors,
            'label': blabel(field, label),
            'break': br and u'<br />' or u'',
            'field': field
        })

@register.filter
def blabel(field, label=None):
    """Outputs the <label> tag of a given field.
    The tag will have the `hasError` class if the field has errors.
    Its output can be chained to the bwrap filter to combine them."""
    
    return BLabeledField(field, label)


@register.filter
def bwrap(field, break_after_label=False):
    """Wraps a field, its label and errors into a <div>.
    The text of the label can also be customized.
    Its output can be chained to the bfilter filter to combine them."""
    
    return BWrappedField(field, break_after_label)
