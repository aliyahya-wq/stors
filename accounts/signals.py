from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .utils import log_activity
from django.db.models.signals import post_migrate
from django.core.management import call_command


CustomUser = get_user_model()


@receiver(post_save, sender=CustomUser)
def log_user_save(sender, instance, created, **kwargs):
    action = 'إنشاء مستخدم' if created else 'تحديث مستخدم'
    log_activity(instance, action, 'CustomUser', instance.id,
                 {'email': instance.email, 'first_name': instance.first_name, 'last_name': instance.last_name})


@receiver(post_delete, sender=CustomUser)
def log_user_delete(sender, instance, **kwargs):
    log_activity(instance, 'حذف مستخدم', 'CustomUser', instance.id,
                 {'email': instance.email, 'first_name': instance.first_name, 'last_name': instance.last_name})


@receiver(post_migrate)
def create_sample_data(sender, **kwargs):
    """
    إنشاء البيانات الافتراضية تلقائياً بعد عمل migrate
    """
    if sender.name == 'accounts':
        # تجنب التنفيذ المزدوج
        from accounts.models import CustomUser
        if not CustomUser.objects.exists():
            call_command('create_sample_data')
