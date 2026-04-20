from django.contrib.auth.models import BaseUserManager

{# مدير المستخدمين المخصص: يتحكم في كيفية إنشاء المستخدمين والمسؤولين داخل النظام باستخدام البريد الإلكتروني بدلاً من اسم المستخدم #}

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        # التحقق من وجود البريد الإلكتروني كشرط أساسي لإنشاء الحساب
        if not email:
            raise ValueError('يجب تقديم البريد الإلكتروني')
        
        # توحيد تنسيق البريد الإلكتروني (مثل تحويل الحروف للصغيرة) لضمان عدم التكرار
        email = self.normalize_email(email)
        
        # إنشاء كائن المستخدم مع البيانات الإضافية الممررة
        user = self.model(email=email, **extra_fields)
        
        # تشفير كلمة المرور قبل حفظها في قاعدة البيانات للحماية الأمنية
        user.set_password(password)
        
        # حفظ المستخدم في قاعدة البيانات الحالية
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        # تعيين الخصائص الافتراضية للمسؤول العام (Superuser)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        # التأكد من صحة الصلاحيات الممنوحة للمسؤول العام
        if extra_fields.get('is_staff') is not True:
            raise ValueError('المدير العام يجب أن يكون is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('المدير العام يجب أن يكون is_superuser=True.')

        # استخدام دالة create_user الأساسية لإتمام عملية الإنشاء
        return self.create_user(email, password, **extra_fields)