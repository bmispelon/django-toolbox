from django.core.mail import EmailMessage
from django.template import Template, Context
from django.template.loader import get_template


class EmailTemplate(object):
    """
    A declarative style email template.
    
    It supports the same fields as django.core.mail.EmailMessage:
        subject, body, from_email, to, cc, bcc, headers.
    
    Each field can be specified in three different ways:
        1. As an attribute on the class for static values.
        2. As a %s_template attribute on the class for simple dynamic values:
            the attribute is considered a template and will be evaluated with
            the proper context when calling the `render` method.
        3. As a %s_template_name attribute on the class for more complex values:
            it looks for a template with the given name and renders it
            with the right context when calling `render()`.
    
    For more complex worflows, subclasses can extend the render_%s methods.
    
    Also note that some fields accept both a value (or a template)
    or a list of them: to, cc, bcc and headers.
    
    
    Example:
    
    class MyEmailTemplate(EmailTemplate):
        subject = 'Welcome to my site!'
        from_email_template = 'Me <{{ site.from_email }}>'
        to_template = '{{ user.name }} <{{ user.email }}>'
        bcc_template = [
            'John Doe {{ site.john_email }}',
            'Jean dupont {{ site.jean_email }}'
        ]
        body_template_name = 'myapp/welcome_email.txt'
    """
    message_class = EmailMessage
    
    def get_message_class(self, context):
        return self.message_class
    
    def render(self, context=None):
        """
        Instanciate an email message with the given context.
        """
        if context is None:
            context = {}
        
        message_class = self.get_message_class(context)
        return message_class(**self._render_kwargs(context))
    
    def render_subject(self, context):
        return self._render_attr('subject', context, single=True)
    
    def render_body(self, context):
        return self._render_attr('body', context, single=True)
    
    def render_from_email(self, context):
        return self._render_attr('from_email', context, single=True)
    
    def render_to(self, context):
        return self._render_attr('to', context, single=False)
    
    def render_cc(self, context):
        return self._render_attr('cc', context, single=False)
    
    def render_bcc(self, context):
        return self._render_attr('bcc', context, single=False)
    
    def render_headers(self, context):
        return self._render_attr('headers', context, single=False)
    
    def _render_kwargs(self, context):
        """
        Return a dictionary of keyword arguments used to instanciate the email object.
        """
        args = ['subject', 'body', 'from_email', 'to', 'cc', 'bcc', 'headers']
        
        return dict((arg, getattr(self, 'render_%s' % arg)(context)) for arg in args)
    
    def _render_attr(self, attr, context, single=True, strip=True):
        """
        Return the value of a given attribute within the context.
        If single is True, multiple lines in the value will be joined by a space.
        If strip is True, lines in the value are stripped.
        """
        value, is_template = self._fetch_attr(attr)
        
        if value is None:
            return None
        
        if is_template:
            value = value.render(Context(context))
        
        # At this point, value is always a string
        assert isinstance(value, basestring)
        
        lines = value.split('\n')
        if strip:
            lines = [line.strip() for line in lines]
        
        if single:
            return ' '.join(lines)
        else:
            return lines
    
    def _fetch_attr(self, attr):
        """
        Try to return a value or a template for a given attribute.
        Return a tuple (x, y) where x is the value or a template object and
        y is a boolean indicating if x is a template object.
        
        The order in which atributes are looked up is the following:
            1. %s_template_name: The name of a template that can be found by django's template machinery.
            2. %s_template: A string template (or a list of them).
            3. %s: A value (or a list of values).
        """
        template_name, template, value = (
            getattr(self, '%s_template_name' % attr, None),
            getattr(self, '%s_template' % attr, None),
            getattr(self, attr, None),
        )
        
        if template_name is not None:
            return get_template(template_name), True
            
        if template is not None:
            if not isinstance(template, basestring):
                template = "\n".join(template)
            return Template(template), True
            
        if not isinstance(value, basestring) and value is not None:
            value = "\n".join(value)
        return value, False
