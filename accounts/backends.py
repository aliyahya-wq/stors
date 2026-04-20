from django.contrib.auth.backends import ModelBackend
from .models import CustomUser

class CustomAuthBackend(ModelBackend):
    """
    محرك مصادقة مخصص (Authentication Backend) يسمح بتسجيل الدخول باستخدام البريد الإلكتروني.
    يرث من ModelBackend الافتراضي لدجانغو مع تعديل منطق العثور على المستخدم.
    """
    def authenticate(self, request, email=None, password=None, **kwargs):  # إعادة تعريف دالة المصادقة الأساسية
        """
        محاولة العثور على المستخدم عبر البريد الإلكتروني والتحقق من كلمة مروره.
        """
        try:
            # البحث عن المستخدم في قاعدة البيانات باستخدام البريد الإلكتروني
            user = CustomUser.objects.get(email=email)  # محاولة جلب كائن المستخدم الذي يطابق البريد الإلكتروني المدخل
            
            # التحقق من صحة كلمة المرور وأن الحساب مسموح له بالدخول (نشط)
            if user.check_password(password) and self.user_can_authenticate(user):  # فحص تشفير كلمة السر وحالة الحساب
                return user  # إرجاع كائن المستخدم في حال نجاح المطابقة
        except CustomUser.DoesNotExist:
            # في حال عدم وجود المستخدم، نرجع None
            return None  # حماية النظام من الفشل عند عدم العثور على الإيميل
        return None  # إرجاع لا شيء في حال فشل أي شرط من شروط التحقق

    def user_can_authenticate(self, user):
        """
        التحقق مما إذا كان المستخدم نشطاً (is_active) قبل السماح له بالدخول.
        """
        return user.is_active  # التأكد من أن الحقل 'is_active' قيمته True في قاعدة البيانات