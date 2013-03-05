from django.utils.translation import ugettext_lazy as _
from django.utils.functional import curry
from django.contrib.messages import api as messages_api


class MessageWrapper(object):
    """Wrap the django.contrib.messages.api module to automatically pass a given
    request object as the first parameter of function calls.
    
    """
    def __init__(self, request):
        self.request = request
    
    def __getattr__(self, attr):
        """Retrieve the function in the messages api and curry it with the
        instance's request.
        
        """
        fn = getattr(messages_api, attr)
        return curry(fn, self.request)


class MessageMixin(object):
    """Add a `messages` attribute on the view instance that wraps
    `django.contrib .messages`, automatically passing the current request object.
    
    """
    def dispatch(self, request, *args, **kwargs):
        self.messages = MessageWrapper(request)
        return super(MessageMixin, self).dispatch(request, *args, **kwargs)


class FormMessageMixin(MessageMixin):
    """Add contrib.messages support in views that use FormMixin."""
    form_valid_message = _("Your form has been saved successfully.")
    form_invalid_message = _("Please correct the errors in the form then re-submit.")
    
    def form_valid(self, form):
        response = super(FormMessageMixin, self).form_valid(form)
        if self.form_valid_message:
            self.messages.success(self.form_valid_message)
        return response
    
    def form_invalid(self, form):
        response = super(FormMessageMixin, self).form_invalid(form)
        if self.form_invalid_message:
            self.messages.error(self.form_invalid_message)
        return response


class DeleteMessageMixin(MessageMixin):
    """Provide message support to generic.DeleteView."""
    
    @property
    def delete_message(self):
        msg = _("The %(object_name)s has been deleted.")
        return msg % {'object_name': self.model._meta.verbose_name}
    
    def delete(self, request, *args, **kwargs):
        response = super(DeleteMessageMixin, self).delete(request, *args, **kwargs)
        self.messages.success(self.delete_message)
        return response
