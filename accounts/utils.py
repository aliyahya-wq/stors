def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def log_activity(user, action, model, object_id, details, request=None):
    from .models import ActivityLog
    ip_address = get_client_ip(request) if request else '0.0.0.0'

    ActivityLog.objects.create(
        user=user,
        action=action,
        model=model,
        object_id=object_id,
        details=details,
        ip_address=ip_address
    )