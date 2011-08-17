from django.forms.forms import Form, BoundField
from django.forms.fields import Field
from django.forms.widgets import Widget
from django.forms.formsets import BaseFormSet, formset_factory
from django.core.exceptions import ValidationError


class FormWithFormsetField(Form):
    def _boundfield(self, field, name):
        if isinstance(field, FormsetField):
            return BoundFormsetField(self, field, name)
        return BoundField(self, field, name)

    def __iter__(self):
        for name, field in self.fields.items():
            yield self._boundfield(self, field, name)

    def __getitem__(self, name):
        "Returns a BoundField with the given name."
        try:
            field = self.fields[name]
        except KeyError:
            raise KeyError('Key %r not found in Form' % name)
        return self._boundfield(field, name)


class FormsetWidget(Widget):
    formset_class = None
    def value_from_datadict(self, data, files, html_name):
        return self.get_formset(data=data, files=files, prefix=html_name)
    
    def get_formset(self, **kwargs):
        return self.formset_class(**kwargs)


class FormsetField(Field):
    widget = FormsetWidget
    def __init__(self, form, formset=BaseFormSet, extra=1, max_num=None, **kwargs):
        super(FormsetField, self).__init__(**kwargs)
        self.widget.formset_class = formset_factory(form, formset, extra, max_num)
    
    def clean(self, formset):
        if formset.is_valid():
            return formset.cleaned_data
        raise ValidationError('Invalid formset')


class BoundFormsetField(BoundField):
    def __init__(self, form, field, name):
        super(BoundFormsetField, self).__init__(form, field, name)
        if not form.is_bound:
            self.formset = field.widget.get_formset(
                prefix=form.add_prefix(name),
                initial=form.initial.get(name, field.initial),
            )
        else:
            self.formset = field.widget.get_formset(
                data=form.data,
                files=form.files,
                prefix=form.add_prefix(name),
            )
    
    def __unicode__(self):
        raise NotImplementedError

    def as_widget(self, widget=None, attrs=None, only_initial=False):
        raise NotImplementedError

    def label_tag(self, contents=None, attrs=None):
        raise NotImplementedError

    def css_classes(self, extra_classes=None):
        raise NotImplementedError

    def _is_hidden(self):
        return False
    is_hidden = property(_is_hidden)

    def _auto_id(self):
        return ''
    auto_id = property(_auto_id)

    def _id_for_label(self):
        raise NotImplementedError
    id_for_label = property(_id_for_label)
    
    def __iter__(self):
        return self.formset.__iter__()
