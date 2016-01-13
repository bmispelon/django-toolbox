"""
A collection of template filters to cutomize form elements inside templates.
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
</div>"""

FIELDWRAPPER_TPL_NO_LABEL = u"""
<div class="%(wrapper_class)s">
    %(errors)s
    %(field)s
</div>"""

DEFAULT_WRAPPER_CLASS = 'fieldWrapper'



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
    def __init__(self, field, br=False, klass=None, show_label=True):
        self.field = field
        self.br = br
        self.klass = klass
        self.show_label = show_label 
    
    def __unicode__(self):
        field = self.field
        br = self.br
        
        if isinstance(field, BLabeledField):
            label = field.label
            field = field.field
        else:
            label = None
        
        return self.render(field, label=label, br=br, klass=self.klass, show_label=self.show_label)
    
    def render(self, field, label=None, br=False, klass=None, show_label=True):
        if klass is None:
            klass = DEFAULT_WRAPPER_CLASS

        if show_label == False:
            return mark_safe(FIELDWRAPPER_TPL_NO_LABEL % {
                'errors': field.errors,
                'label': blabel(field, label),
                'break': br and u'<br />' or u'',
                'field': field,
                'wrapper_class': klass
            })
        
        return mark_safe(FIELDWRAPPER_TPL % {
            'errors': field.errors,
            'label': blabel(field, label),
            'break': br and u'<br />' or u'',
            'field': field,
            'wrapper_class': klass
        })


class BClassedField(object):
    """A small class that allows adding custom css classes to form fields.
    If the item passed is a regular django field, the class will be added to it.
    If it's an instance of BWrappedField, the class is added to the fieldWrapper.'"""
    def __init__(self, field, klass):
        self.field, self.klass = field, klass
    
    def __unicode__(self):
        klass = self.make_class()
        field = self.field
        if isinstance(field, BWrappedField):
            field.klass = klass
            return field.__unicode__()
        return field.as_widget(attrs={'class': klass})
    
    def make_class(self):
        l = self.klass.strip().split()
        if isinstance(self.field, BWrappedField):
            l.append(DEFAULT_WRAPPER_CLASS)
        return ' '.join(l)

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


@register.filter
def bwrap_no_label(field):
    """Wraps a field and its errors into a <div> without label.
    The text of the label can also be customized."""
    
    return BWrappedField(field, show_label=False)


@register.filter
def bclass(field, extra_class):
    """Adds a css class to either a django form field or a wrapped field."""
    return BClassedField(field, extra_class)
