from django.template import Node, Library
from django.template.base import VariableDoesNotExist
from django.template.defaulttags import TemplateIfParser
from django.utils.safestring import mark_safe

register = Library()

class BallotNode(Node):
    def __init__(self, var):
        self.var = var
    
    def render(self, context):
        try:
            var = self.var.eval(context)
        except VariableDoesNotExist:
            var = None
        
        if var:
            return '&#9746;'
        else:
            return '&#9744;'


@register.tag
def ballot(parser, token):
    bits = token.split_contents()[1:]
    var = TemplateIfParser(parser, bits).parse()
    
    return BallotNode(var)
