from django.template.base import VariableDoesNotExist
from django.template import Library

register = Library()

@register.simple_tag
def ballot(var):
    if var:
        return '&#9746;'
    else:
        return '&#9744;'
