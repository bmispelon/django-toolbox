from django.core.urlresolvers import reverse
from django.core.exceptions import ImproperlyConfigured
from django.views import generic

class NextMixin(object):
    default_next_urlname = None
    next_field_name = 'next'
    next_context_name = 'next'
    
    def get_default_next_url(self):
        if self.default_next_urlname is None:
            raise ImproperlyConfigured('No default URL to redirect to.')
        return reverse(self.default_next_urlname)
    
    def get_success_url(self):
        next = self.request.REQUEST.get(self.next_field_name)
        return next or self.get_default_next_url()


class CreateView(NextMixin, generic.CreateView):
    def get_context_data(self, **kwargs):
        context = super(CreateView, self).get_context_data(**kwargs)
        context[self.next_context_name] = self.get_success_url()
        
        return context


class UpdateView(NextMixin, generic.UpdateView):
    def get_context_data(self, **kwargs):
        context = super(UpdateView, self).get_context_data(**kwargs)
        context[self.next_context_name] = self.get_success_url()
        
        return context


class DeleteView(NextMixin, generic.DeleteView):
    def get_context_data(self, **kwargs):
        context = super(DeleteView, self).get_context_data(**kwargs)
        context[self.next_context_name] = self.get_success_url()
        
        return context
