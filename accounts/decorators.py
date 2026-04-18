from django.http import HttpResponseForbidden
from django.contrib import messages
from functools import wraps

def role_required(allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.user.role.name in allowed_roles:
                return view_func(request, *args, **kwargs)
            messages.error(request, "ليس لديك صلاحية للوصول إلى هذه الصفحة.")
            return HttpResponseForbidden()
        return _wrapped_view
    return decorator

def permission_required(permission_codename):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.user.has_perm(permission_codename):
                return view_func(request, *args, **kwargs)
            messages.error(request, "ليس لديك الصلاحية اللازمة لهذا الإجراء.")
            return HttpResponseForbidden()
        return _wrapped_view
    return decorator