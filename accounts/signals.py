from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .utils import log_activity
from django.db.models.signals import post_migrate
from django.core.management import call_command

# الحصول على كود المستخدم المخصص (CustomUser)
CustomUser = get_user_model()  # استرجاع نموذج المستخدم النشط حالياً في إعدادات المشروع


@receiver(post_save, sender=CustomUser)
def log_user_save(sender, instance, created, **kwargs):
    """
    إشارة (Signal) يتم تفعيلها فور حفظ كائن المستخدم في قاعدة البيانات.
    تقوم بتسجيل ما إذا كانت العملية إضافة مستخدم جديد أو تحديث بيانات مستخدم موجود.
    """
    action = 'إنشاء مستخدم' if created else 'تحديث مستخدم'  # التحقق من حالة 'created' لتحديد نوع العملية
    # تسجيل النشاط في السجل العام للرقابة
    log_activity(instance, action, 'CustomUser', instance.id,  # استدعاء دالة التدوين مع تمرير البيانات الأساسية
                 {'email': instance.email, 'first_name': instance.first_name, 'last_name': instance.last_name})  # تمرير تفاصيل إضافية في قاموس


@receiver(post_delete, sender=CustomUser)
def log_user_delete(sender, instance, **kwargs):
    """
    إشارة يتم تفعيلها فور حذف مستخدم من النظام.
    تضمن وجود سجل لعملية الحذف للرجوع إليها مستقبلاً.
    """
    log_activity(instance, 'حذف مستخدم', 'CustomUser', instance.id,  # تسجيل عملية الحذف قبل مسح الكائن نهائياً من قاعدة البيانات
                 {'email': instance.email, 'first_name': instance.first_name, 'last_name': instance.last_name})  # أرشفة البيانات الأساسية للمستخدم المحذوف


@receiver(post_migrate)
def create_sample_data(sender, **kwargs):
    """
    إشارة يتم تفعيلها بعد الانتهاء من عملية ترحيل قاعدة البيانات (Migrations).
    الهدف هو التأكد من وجود بيانات تجريبية وحسابات افتراضية عند تشغيل النظام لأول مرة.
    """
    if sender.name == 'accounts':  # التحقق من أن التطبيق الذي انتهى ترحيله هو تطبيق 'accounts'
        # نتحقق من اسم التطبيق لتنفيذ الكود مرة واحدة فقط عند تطبيق تغييرات هذا التطبيق
        from accounts.models import CustomUser  # استيراد النموذج محلياً لتجنب مشاكل الاستيراد الدائري
        if not CustomUser.objects.exists():  # التأكد من خلو قاعدة البيانات من المستخدمين قبل البدء
            # إذا لم يكن هناك مستخدمون، يتم استدعاء أمر سطر الأوامر لإنشاء البيانات الأساسية
            call_command('create_sample_data')  # تنفيذ أمر الإدارة المخصص لتوليد البيانات الأولية
