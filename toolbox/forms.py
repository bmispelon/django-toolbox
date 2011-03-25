from django import forms

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
