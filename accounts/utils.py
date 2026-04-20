def get_client_ip(request):
    """
    استخراج عنوان IP الحقيقي للجهاز الذي يقوم بالطلب.
    يتعامل مع عناوين IP سواء كان المستخدم خلف خادم وكيل (Proxy) أو اتصال مباشر.
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')  # التحقق من وجود عناوين ممررة عبر بروكسي
    if x_forwarded_for:  # إذا كان المستخدم يتصل عبر خادم وسيط
        # في حال وجود بروكسي، يكون العنوان الأول هو العنوان الحقيقي للجهاز
        ip = x_forwarded_for.split(',')[0]
        ip = x_forwarded_for.split(',')[0]  # استخراج أول عنوان IP في القائمة (العنوان الأصلي)
    else:
        # الاتصال المباشر
        ip = request.META.get('REMOTE_ADDR')
    return ip
        ip = request.META.get('REMOTE_ADDR')  # الحصول على العنوان المباشر من خصائص الطلب
    return ip  # إرجاع العنوان النهائي


def log_activity(user, action, model, object_id, details, request=None):
    """
    دالة مساعدة لتبسيط عملية تسجيل الأنشطة في قاعدة البيانات.
    يتم استدعاؤها في مختلف الصور (Views) عند حدوث إضافة، تعديل أو حذف.
    """
    from .models import ActivityLog
    # تحديد عنوان الأي بي إذا تيسر وجود كائن الطلب (request)
    ip_address = get_client_ip(request) if request else '0.0.0.0'

    # إنشاء سجل النشاط في قاعدة البيانات
    ActivityLog.objects.create(
        user=user,
        action=action,
        model=model,
        object_id=object_id,
        details=details,
        ip_address=ip_address
    )