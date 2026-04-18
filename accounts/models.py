from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('يجب تقديم البريد الإلكتروني')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class Permission(models.Model):
    name = models.CharField(max_length=100, verbose_name="اسم الصلاحية")
    codename = models.CharField(max_length=100, unique=True, verbose_name="كود الصلاحية")
    module = models.CharField(max_length=50, verbose_name="الوحدة")
    description = models.TextField(verbose_name="الوصف")

    class Meta:
        verbose_name = "صلاحية"
        verbose_name_plural = "الصلاحيات"

    def __str__(self):
        return self.name


class UserRole(models.Model):
    ROLE_CHOICES = [
        ('super_admin', 'المدير العام'),
        ('admin', 'مدير النظام'),
        ('inventory_manager', 'مدير المخازن'),
        ('purchase_manager', 'مدير المشتريات'),
        ('sales_manager', 'مدير المبيعات'),
        ('viewer', 'مشاهد'),
    ]

    name = models.CharField(max_length=50, choices=ROLE_CHOICES, verbose_name="اسم الدور")
    permissions = models.ManyToManyField(Permission, blank=True, verbose_name="الصلاحيات")
    description = models.TextField(verbose_name="الوصف")

    class Meta:
        verbose_name = "دور المستخدم"
        verbose_name_plural = "أدوار المستخدمين"

    def __str__(self):
        return self.get_name_display()


class CustomUser(AbstractUser):
    username = None
    email = models.EmailField(unique=True, verbose_name="البريد الإلكتروني")
    role = models.ForeignKey(UserRole, on_delete=models.PROTECT, verbose_name="الدور")
    phone = models.CharField(max_length=20, verbose_name="رقم الهاتف")
    department = models.CharField(max_length=100, verbose_name="القسم")
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    last_login = models.DateTimeField(null=True, blank=True, verbose_name="آخر تسجيل دخول")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        verbose_name = "مستخدم"
        verbose_name_plural = "المستخدمين"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def has_perm(self, perm, obj=None):
        return self.role.permissions.filter(codename=perm).exists()

    def has_module_perms(self, app_label):
        return True


class ActivityLog(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name="المستخدم")
    action = models.CharField(max_length=100, verbose_name="الإجراء")
    model = models.CharField(max_length=50, verbose_name="النموذج")
    object_id = models.IntegerField(verbose_name="معرف الكائن")
    details = models.JSONField(default=dict, verbose_name="التفاصيل")
    ip_address = models.GenericIPAddressField(verbose_name="عنوان IP")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="الوقت")

    class Meta:
        verbose_name = "سجل النشاط"
        verbose_name_plural = "سجلات الأنشطة"
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user} - {self.action}"
