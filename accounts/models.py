from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _


class CustomUserManager(BaseUserManager):
    """
    مدير مخصص للمستخدمين حيث يتم استخدام البريد الإلكتروني كمعرف فريد بدلاً من اسم المستخدم.
    """
    def create_user(self, email, password=None, **extra_fields):  # دالة إنشاء مستخدم عادي
        # التحقق من وجود البريد الإلكتروني لأنه إلزامي
        if not email:  # فحص منطقي للتأكد من أن البريد ليس فارغاً
            raise ValueError('يجب تقديم البريد الإلكتروني')  # إيقاف العملية وإظهار خطأ في حال غيابه
        
        # تنظيف البريد الإلكتروني وتوحيد تنسيقه
        email = self.normalize_email(email)  # تحويل الجزء الخاص بالنطاق في الإيميل إلى حروف صغيرة (Standardization)
        
        # إنشاء كائن المستخدم وتعيين كلمة المرور المشفرة
        user = self.model(email=email, **extra_fields)  # بناء الكائن مع الحقول الإضافية الممررة
        user.set_password(password)  # استخدام دالة دجانغو الآمنة لتشفير كلمة السر (Hashing)
        user.save(using=self._db)  # حفظ الكائن في قاعدة البيانات النشطة
        return user  # إرجاع المستخدم المنشأ

    def create_superuser(self, email, password=None, **extra_fields):  # دالة إنشاء المدير الخارق (صلاحيات كاملة)
        # إعداد الحقول الافتراضية للمدير الخارق (superuser)
        extra_fields.setdefault('is_staff', True)  # منح حق دخول لوحة الإدارة تلقائياً
        extra_fields.setdefault('is_superuser', True)  # منح كافة الصلاحيات دون استثناء
        return self.create_user(email, password, **extra_fields)  # استدعاء الدالة الأساسية لإكمال الإنشاء


class Permission(models.Model):
    """
    نموذج لتمثيل الصلاحيات في النظام بشكل مخصص بدلاً من صلاحيات دجانغو الافتراضية.
    تستخدم للتحكم الدقيق في العمليات البرمجية داخل الوحدات المختلفة.
    """
    name = models.CharField(max_length=100, verbose_name="اسم الصلاحية")  # الاسم المعروض للمسؤول
    codename = models.CharField(max_length=100, unique=True, verbose_name="كود الصلاحية")  # المعرف البرمجي المستخدم في الأكواد
    module = models.CharField(max_length=50, verbose_name="الوحدة")  # اسم التطبيق أو الوحدة (مخازن، مبيعات، إلخ)
    description = models.TextField(verbose_name="الوصف")  # وصف مفصل لما تسمح به هذه الصلاحية

    class Meta:
        verbose_name = "صلاحية"
        verbose_name_plural = "الصلاحيات"

    def __str__(self):
        return self.name


class UserRole(models.Model):
    """
    نموذج لتحديد أدوار المستخدمين ومجموعة الصلاحيات المرتبطة بكل دور.
    يسمح بتصنيف المستخدمين (مدير، محاسب، إلخ) وتعيين صلاحياتهم دفعة واحدة.
    """
    ROLE_CHOICES = [
        ('super_admin', 'المدير العام'),
        ('admin', 'مدير النظام'),
        ('inventory_manager', 'مدير المخازن'),
        ('purchase_manager', 'مدير المشتريات'),
        ('sales_manager', 'مدير المبيعات'),
        ('viewer', 'مشاهد'),
    ]

    name = models.CharField(max_length=50, choices=ROLE_CHOICES, verbose_name="اسم الدور")
    permissions = models.ManyToManyField(Permission, blank=True, verbose_name="الصلاحيات")  # علاقة متعدد إلى متعدد مع الصلاحيات
    description = models.TextField(verbose_name="الوصف")

    class Meta:
        verbose_name = "دور المستخدم"
        verbose_name_plural = "أدوار المستخدمين"

    def __str__(self):
        return self.get_name_display()  # إرجاع الاسم المقروء (مثل 'المدير العام') بدلاً من الكود


class CustomUser(AbstractUser):
    """
    الموديل الأساسي للمستخدم في النظام. 
    يرث من AbstractUser لإضافة حقول مخصصة مثل الدور (Role) والقسم (Department).
    """
    username = None  # تم إلغاء اسم المستخدم والاعتماد على البريد الإلكتروني
    email = models.EmailField(unique=True, verbose_name="البريد الإلكتروني")
    role = models.ForeignKey(UserRole, on_delete=models.PROTECT, verbose_name="الدور")  # ربط المستخدم بدور معين
    phone = models.CharField(max_length=20, verbose_name="رقم الهاتف")
    department = models.CharField(max_length=100, verbose_name="القسم")
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    last_login = models.DateTimeField(null=True, blank=True, verbose_name="آخر تسجيل دخول")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")

    objects = CustomUserManager()  # ربط النموذج بالمدير المخصص للتعامل مع البريد الإلكتروني

    USERNAME_FIELD = 'email'  # إخبار دجانغو أن البريد الإلكتروني هو المعرف الرئيسي بدلاً من 'username'
    REQUIRED_FIELDS = ['first_name', 'last_name']  # الحقول الإلزامية التي يطلبها سطر الأوامر (createsuperuser)

    class Meta:
        verbose_name = "مستخدم"
        verbose_name_plural = "المستخدمين"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property  # تحويل الدالة إلى خاصية يمكن الوصول إليها كمتغير (user.is_super_admin)
    def is_super_admin(self):
        return self.role.name == 'super_admin'  # مقارنة نصية مع اسم الدور المسجل

    @property  # خاصية مجمعة للمستويات الإدارية العليا
    def is_admin(self):
        return self.role.name in ['super_admin', 'admin']  # التحقق من وجود الدور ضمن مصفوفة الأدوار القيادية

    def has_perm(self, perm, obj=None):  # تخصيص منطق فحص الصلاحيات الافتراضي لدجانغو
        if self.is_admin:
            return True  # السماح التلقائي للمدراء (Bypass permission check)
        return self.role.permissions.filter(codename=perm).exists()  # فحص قاعدة البيانات بحثاً عن الصلاحية المطلوبة لهذا الدور تحديداً

    def has_module_perms(self, app_label):
        return True


class ActivityLog(models.Model):
    """
    نموذج لتسجيل كافة الأنشطة الهامة التي يقوم بها المستخدمون في النظام.
    يستخدم لأغراض الرقابة وتتبع العمليات (Audit Trail).
    """
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name="المستخدم")
    action = models.CharField(max_length=100, verbose_name="الإجراء")  # نوع الإجراء (إضافة، تعديل، حذف، إلخ)
    model = models.CharField(max_length=50, verbose_name="النموذج")  # اسم الجدول المتأثر
    object_id = models.IntegerField(verbose_name="معرف الكائن")  # رقم المعرف للكائن المتأثر
    details = models.JSONField(default=dict, verbose_name="التفاصيل")  # تفاصيل إضافية عن التغييرات بتنسيق JSON
    ip_address = models.GenericIPAddressField(verbose_name="عنوان IP")  # عنوان الأي بي للجهاز الذي قام بالعملية
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="الوقت")

    class Meta:
        verbose_name = "سجل النشاط"
        verbose_name_plural = "سجلات الأنشطة"
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user} - {self.action}"
