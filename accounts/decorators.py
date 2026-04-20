from django.http import HttpResponseForbidden
from django.contrib import messages
from functools import wraps

def role_required(allowed_roles):
    """
    ديكوريتور (Decorator) مخصص للتحقق من دور المستخدم قبل السماح له بالوصول للدالة (View).
    يأخذ قائمة بالأدوار المسموح لها بالدخول.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # يتم السماح بالدخول تلقائياً إذا كان المستخدم مديراً (نظام أو عام)
            # أو إذا كان اسم دوره موجود ضمن قائمة الأدوار الممررة للدالة
            if request.user.is_admin or request.user.role.name in allowed_roles:
                return view_func(request, *args, **kwargs)  # تنفيذ الدالة الأصلية بنجاح
            
            # في حال عدم توفر الصلاحية، يتم عرض رسالة خطأ ومنع الوصول
            messages.error(request, "ليس لديك صلاحية للوصول إلى هذه الصفحة.")
            return HttpResponseForbidden()
        return _wrapped_view
    return decorator

def permission_required(permission_codename):
    """
    ديكوريتور للتحقق من امتلاك المستخدم لصلاحية محددة بناءً على 'كود الصلاحية'.
    صمم لاستخدامه فوق الدوال للتحكم الدقيق في الوصول للعمليات.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # المديرين يملكون كافة الصلاحيات تلقائياً، وغيرهم يتم فحص صلاحياته المسجلة
            if request.user.is_admin or request.user.has_perm(permission_codename):
                return view_func(request, *args, **kwargs)  # السماح بعرض الصفحة أو تنفيذ العملية
            
            # رسالة تنبيه للمستخدم غير المصرح له
            messages.error(request, "ليس لديك الصلاحية اللازمة لهذا الإجراء.")
            return HttpResponseForbidden()
        return _wrapped_view
    return decorator