from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.utils.encoding import smart_str
from django.views.generic import DetailView

import jingo
from session_csrf import anonymous_csrf


class JingoResponseMixin(object):

    def render_to_response(self, context, **response_kwargs):
        return jingo.render(self.request, self.get_template_names()[0], context,
                            **response_kwargs)


class AnonymousCSRF(object):

    @method_decorator(anonymous_csrf)
    def dispatch(self, *args, **kwargs):
        return super(AnonymousCSRF, self).dispatch(*args, **kwargs)


class AdminRequiredMixin(object):

    @method_decorator(staff_member_required)
    def dispatch(self, *args, **kwargs):
        return super(AdminRequiredMixin, self).dispatch(*args, **kwargs)


class LoginRequiredMixin(object):

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(*args, **kwargs)


class ChildMixin(object):
    
    parent = None
    parent_model = None
    parent_slug_field = 'slug'
    parent_slug_url_kwarg = 'parent_slug'
    parent_pk_url_kwarg = 'parent_pk'
    parent_context_object_name = None
    
    def get_parent_context_object_name(self, obj):
        """
        Get the name to use for the object.
        """
        if self.parent_context_object_name:
            return self.parent_context_object_name
        elif hasattr(obj, '_meta'):
            return smart_str(obj._meta.object_name.lower())
        else:
            return None
    
    def get_parent(self):
        if not self.parent:
            parent_slug = self.kwargs.get(self.parent_slug_url_kwarg, None)
            parent_pk = self.kwargs.get(self.parent_pk_url_kwarg, None)
            parent_id = self.kwargs.get('parent_id', None)
            kwargs = {}
            if parent_slug:
                kwargs[self.parent_slug_field] = parent_slug
            elif parent_pk:
                kwargs['pk'] = parent_pk
            else:
                kwargs['id'] = parent_id
            self.parent = get_object_or_404(self.parent_model, **kwargs)
        return self.parent
        
    def get_context_data(self, *args, **kwargs):
        context = super(ChildMixin, self).get_context_data(*args, **kwargs)
        # Had to do this for the form views, which don't call get_queryset()
        if not self.parent:
            self.get_parent()
        self.parent_context_object_name = self.get_parent_context_object_name(self.parent)
        context[self.parent_context_object_name] = self.parent
        return context
        

class ChildFormMixin(ChildMixin):
    
    parent_field_name = None
    
    def get_parent_field_name(self):
        if self.parent_field_name:
            return self.parent_field_name
        self.get_parent()
        self.parent_field_name = self.get_parent_context_object_name(self.parent)
        return self.parent_field_name
    
    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.get_parent()
        setattr(self.object, self.get_parent_field_name(), self.parent)
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())


class AjaxMixin(object):
    
    def get(self, request, *args, **kwargs):
        if request.is_ajax():
            self.template_name_suffix += '_ajax'
        return super(AjaxMixin, self).get(request, *args, **kwargs)
