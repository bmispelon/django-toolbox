from django import forms

class ForcedValueModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self._forced_values = kwargs.pop('forced', {})
        super(ForcedValueModelForm, self).__init__(*args, **kwargs)
    
    def clean(self, *args, **kwargs):
        for k, v in self._forced_values.items():
            setattr(self.instance, k, v)
        return super(ForcedValueModelForm, self).clean(*args, **kwargs)
