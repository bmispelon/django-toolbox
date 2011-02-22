from django.core.mail import EmailMessage
from django.template import Template, Context
from django.template.loader import get_template

class EmailTemplate(object):
    def render(self, context):
        return EmailMessage(**self._render_kwargs(context))
    
    def _render_kwargs(self, context):
        context = Context(context)
        text_fields = ('subject', 'body', 'from_email')
        list_fields = ('to', 'cc', 'bcc', 'headers')
        
        data = [(f, self._get_attr(f, context)) for f in text_fields] +\
                [(f, self._get_attr(f, context, True)) for f in list_fields]
        
        return dict(data)
        
    
    def _get_raw(self, attr):
        template_name, template, value = (
            getattr(self, '%s_template_name' % attr, None),
            getattr(self, '%s_template' % attr, None),
            getattr(self, attr, None),
        )
        
        if template_name is not None:
            return get_template(template_name)
            
        if template is not None:
            if hasattr(template, '__iter__'):
                template = "\n".join(template)
            return Template(template)
            
        if hasattr(value, '__iter__'):
            value = "\n".join(value)
        return value
    
    def _get_rendered(self, attr, context):
        raw = self._get_raw(attr)
        try:
            return raw.render(context)
        except AttributeError:
            return raw
    
    def _get_attr(self, attr, context, is_list=False):
        value = self._get_rendered(attr, context)
        if not is_list:
            return value
        if value is None:
            return []
        return [e.strip() for e in value.split("\n")]
