from django.forms.fields import CharField
from toolbox.text import smartish_split
from django.utils.encoding import smart_unicode

class MultipleKeywordsSearchField(CharField):
    # TODO: stopwords
    def to_python(self, value):
        return [smart_unicode(bit) for bit in smartish_split(value)]
