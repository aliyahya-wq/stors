from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib import messages
from django.shortcuts import redirect


class RoleRequiredMixin(UserPassesTestMixin):
    allowed_roles = []

    def test_func(self):
        return self.request.user.role.name in self.allowed_roles

    def handle_no_permission(self):
        messages.error(self.request, "ليس لديك صلاحية للوصول إلى هذه الصفحة.")
        return redirect('accounts:dashboard')


class SuperAdminRequiredMixin(RoleRequiredMixin):
    allowed_roles = ['super_admin']


class AdminRequiredMixin(RoleRequiredMixin):
    allowed_roles = ['super_admin', 'admin']


class ManagerRequiredMixin(RoleRequiredMixin):
    allowed_roles = ['super_admin', 'admin', 'inventory_manager', 'purchase_manager', 'sales_manager']