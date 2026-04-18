from django.db import models
from django.conf import settings

class Notification(models.Model):
    LEVEL_CHOICES = [
        ('info', 'معلومات'),
        ('success', 'نجاح'),
        ('warning', 'تحذير'),
        ('danger', 'خطر'),
    ]

    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications', verbose_name="المستلم")
    title = models.CharField(max_length=255, verbose_name="العنوان")
    message = models.TextField(verbose_name="الرسالة")
    level = models.CharField(max_length=10, choices=LEVEL_CHOICES, default='info', verbose_name="المستوى")
    is_read = models.BooleanField(default=False, verbose_name="مقروءة")
    link = models.CharField(max_length=500, blank=True, null=True, verbose_name="رابط")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")

    class Meta:
        verbose_name = "إشعار"
        verbose_name_plural = "الإشعارات"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.recipient.username}"
