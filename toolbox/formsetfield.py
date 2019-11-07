from django.forms.forms import Form, BoundField
from django.forms.fields import Field
from django.forms.widgets import Widget
from django.forms.formsets import BaseFormSet, formset_factory
from django.core.exceptions import ValidationError
from django.utils.encoding import python_2_unicode_compatible


class FormWithFormsetField(Form):
    pass  # Only kept for legacy reason
    # TODO: remove this class


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

    def get_bound_field(self, form, field_name):
        return BoundFormsetField(form, self, field_name)


@python_2_unicode_compatible
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
    
    def __str__(self):
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
