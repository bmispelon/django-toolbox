from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.views import generic


class NextMixin(object):
    """A mixin for generic CBV that defines get_success_url to take into account
    a parameter in the request.
    If that parameter is not present, or is empty, fall back to a default URL.
    If that default parameter is empty, use the request's referer header.
    """
    default_next_urlname = None # For backwards compatibility
    default_next_url = None # New views should use this attribute with reverse_lazy
    next_field_name = 'next'
    next_context_name = 'next'
    
    def get_default_next_url(self):
        """Return the fallback URL for when the request contains no redirect
        parameter. If none is defined, use the referer header.
        
        """
        if self.default_next_urlname:
            next = reverse(self.default_next_urlname)
        elif self.default_next_url:
            next = self.default_next_url
        else:
            next = self.request.META['HTTP_REFERER']
        return next
    
    def get_success_url(self):
        """Look for a redirect URL in the request parameters (GET or POST)."""
        field_name = self.next_field_name
        next = self.request.POST.get(field_name, self.request.GET.get(field_name))
        return next or self.get_default_next_url()
    
    def redirect(self):
        """A utility method that returns a 302 HTTP response."""
        return HttpResponseRedirect(self.get_success_url())
    
    def get_context_data(self, **kwargs):
        """Add the computed next URL to the context."""
        context = super(NextMixin, self).get_context_data(**kwargs)
        context[self.next_context_name] = self.get_success_url()
        return context


# The following are left for backwards-compatibility reasons.
# New views should just use the mixin.

class CreateView(NextMixin, generic.CreateView):
    pass


class UpdateView(NextMixin, generic.UpdateView):
    pass


class DeleteView(NextMixin, generic.DeleteView):
    pass
