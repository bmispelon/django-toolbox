from django import forms
from django.utils.safestring import mark_safe

class ForcedValueModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self._forced_values = kwargs.pop('forced', {})
        super(ForcedValueModelForm, self).__init__(*args, **kwargs)
    
    def clean(self, *args, **kwargs):
        for k, v in self._forced_values.items():
            setattr(self.instance, k, v)
        return super(ForcedValueModelForm, self).clean(*args, **kwargs)

class ExtraCleanModelForm(forms.ModelForm):
    def _mark_error(self, field, error, clean_data):
        self._errors[field] = self.error_class([error])
        del clean_data[field]
    
    
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
    A MultiForm class should have a forms property that is an iterable of
    (form_prefix, form_class) tuples.
    """
    
    def __init__(self, *args, **kwargs):
        self.prefix = kwargs.pop('prefix', None)
        self.initial = kwargs.pop('initial', None)
        self.instance = kwargs.pop('instance', None)
        extra_kwargs = kwargs.pop('extra_kwargs', {})

        _l = []
        for name, form_class in self.forms:
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
    
    def get_prefix(self, name):
        if self.prefix is None:
            return name
        else:
            return '%s-%s' % (global_prefix, name)
    
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
    
    def save(self):
        # Children class should implement this
        raise NotImplementedError
    
    def as_ul(self):
        return mark_safe('\n'.join(f.as_ul() for _x, f in self.forms))
    
    def __getitem__(self, key):
        return dict(self.forms)[key]
