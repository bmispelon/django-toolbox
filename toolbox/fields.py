from django.forms.fields import CharField, TypedChoiceField, TypedMultipleChoiceField
from toolbox.text import smartish_split
from django.utils.encoding import smart_unicode

class MultipleKeywordsSearchField(CharField):
    # TODO: stopwords
    def to_python(self, value):
        return [smart_unicode(bit) for bit in smartish_split(value)]


class IntegerChoiceField(TypedChoiceField):
    def __init__(self, *args, **kwargs):
        new_kwargs = {
            'coerce': int,
            'empty_value': 0,
        }
        new_kwargs.update(kwargs)
        super(IntegerChoiceField, self).__init__(*args, **new_kwargs)

class MultipleIntegerChoiceField(TypedMultipleChoiceField):
    def __init__(self, *args, **kwargs):
        new_kwargs = {
            'coerce': int,
            'empty_value': 0,
        }
        new_kwargs.update(kwargs)
        super(MultipleIntegerChoiceField, self).__init__(*args, **new_kwargs)
