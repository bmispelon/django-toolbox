from django import forms
from django.utils.safestring import mark_safe
from itertools import chain

class ForcedValueModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self._forced_values = kwargs.pop('forced', {})
        super(ForcedValueModelForm, self).__init__(*args, **kwargs)
    
    def clean(self, *args, **kwargs):
        for k, v in self._forced_values.items():
            setattr(self.instance, k, v)
        return super(ForcedValueModelForm, self).clean(*args, **kwargs)

class ExtraCleanModelForm(forms.ModelForm):
    def clean(self):
        cleaned = self.cleaned_data
        for name, field in self.fields.items():
            try:
                getattr(self, 'x_clean_%s' % name)(cleaned)
            except AttributeError:
                pass
        return cleaned


class MultiForm(object):
    """
    A ducktyped form class that wraps several forms into one entity.
    A MultiForm class should have a forms property (or a get_forms method )
    that is an iterable of (form_name, form_class) tuples.
    """
    
    def __init__(self, *args, **kwargs):
        self.prefix = kwargs.pop('prefix', None)
        self.initial = kwargs.pop('initial', None)
        self.instance = kwargs.pop('instance', None)
        extra_kwargs = kwargs.pop('extra_kwargs', {})

        _l = []
        for name, form_class in self.get_forms():
            k = {
                'prefix': self.get_prefix(name),
                'initial': self.get_initial(name),
            }
            instance = self.get_instance(name)
            if instance is not None:
                k['instance'] = instance
            
            k.update(kwargs)
            k.update(extra_kwargs.get(name, {}))
            
            _l.append((name, form_class(*args, **k)))
        
        self.forms = _l

        combined_initial = {k: f.initial for k, f in self.forms if f.initial is not None}
        if combined_initial:
            self.initial = combined_initial
    
    def get_forms(self):
        """Return an iterable of (form_name, form_class)"""
        return self.forms
    
    def get_prefix(self, name):
        if self.prefix is None:
            return name
        else:
            return '%s-%s' % (self.prefix, name)
    
    def get_initial(self, name):
        if self.initial is None:
            return None
        return self.initial.get(name)
    
    def get_instance(self, name):
        if self.instance is None:
            return None
        return self.instance.get(name)
    
    def is_valid(self):
        return all([f.is_valid() for _x, f in self.forms])
    
    def clean(self):
        [f.clean() for _x, f in self.forms]
    
    @property
    def cleaned_data(self):
        return dict((name, f.cleaned_data) for name, f in self.forms)
    
    @property
    def errors(self):
        return dict((name, f.errors) for name, f in self.forms if f.errors)

    @property
    def is_bound(self):
        return any(f.is_bound for _, f in self.forms)
    
    def save(self):
        # Children class should implement this
        raise NotImplementedError
    
    def _as_foo(self, foo):
        """Render the various as_p, as_ul or as_table method of self.forms."""
        method = 'as_%s' % foo
        rendered = '\n'.join(getattr(f, method)() for _x, f in self.forms)
        return mark_safe(rendered)
    
    def as_ul(self):
        return self._as_foo('ul')
    
    def as_p(self):
        return self._as_foo('p')
    
    def as_table(self):
        return self._as_foo('table')
    
    def __getitem__(self, key):
        return dict(self.forms)[key]
    
    def __iter__(self):
        for _x, form in self.forms:
            for field in form:
                yield field


class BooleanRadioSelect(forms.RadioSelect):
    """A widget to use radio buttons for a BooleanField"""
    def get_renderer(self, name, value, attrs=None, choices=()):
        """Returns an instance of the renderer."""
        if value is None: value = ''
        str_value = value and u"1" or u"0"
        final_attrs = self.build_attrs(attrs)
        choices = list(chain(self.choices, choices))
        return self.renderer(name, str_value, final_attrs, choices)
