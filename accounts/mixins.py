from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib import messages
from django.shortcuts import redirect


class RoleRequiredMixin(UserPassesTestMixin):
    """
    ميكسين (Mixin) للأصناف (Class-based views) للتحقق من الأدوار.
    يرث من UserPassesTestMixin لتنفيذ منطق فحص مخصص.
    """
    allowed_roles = []  # قائمة الأدوار المسموح لها بالوصول وتحتاج لتعريفها في الكلاس الوارث

    def test_func(self):  # الوظيفة المسؤولة عن اختبار صلاحية المستخدم قبل عرض الصفحة
        """
        هذه الدالة يتم استدعاؤها من قبل دجانغو لاختبار الصلاحية.
        إذا أعادت True، يتم السماح بالدخول، وإذا أعادت False يتم استدعاء handle_no_permission.
        """
        # السماح بالدخول تلقائياً للمديرين أو لمن تتوفر أدوارهم في القائمة المسموح بها
        return self.request.user.is_admin or self.request.user.role.name in self.allowed_roles  # فحص الدور البرمجي

    def handle_no_permission(self):  # ماذا يحدث عندما يفشل المستخدم في الاختبار؟
        """
        تحديد الإجراء المتبع في حال فشل اختبار الصلاحية.
        """
        messages.error(self.request, "ليس لديك صلاحية للوصول إلى هذه الصفحة.")  # إظهار رسالة تحذيرية
        return redirect('accounts:dashboard')  # إعادة توجيهه للوحة التحكم الرئيسية كإجراء أمني


class SuperAdminRequiredMixin(RoleRequiredMixin):
    """
    ميكسين مخصص لمنح الصلاحية للمدير العام فقط.
    """
    allowed_roles = ['super_admin']


class AdminRequiredMixin(RoleRequiredMixin):
    """
    ميكسين مخصص للمديرين (العام والنظام).
    """
    allowed_roles = ['super_admin', 'admin']


class ManagerRequiredMixin(RoleRequiredMixin):
    """
    ميكسين للمديرين بكافة تخصصاتهم (مخازن، مبيعات، مشتريات) بالإضافة للمدير العام.
    """
    allowed_roles = ['super_admin', 'admin', 'inventory_manager', 'purchase_manager', 'sales_manager']