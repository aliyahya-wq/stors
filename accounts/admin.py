from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, UserRole, Permission, ActivityLog


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'role', 'department', 'is_active', 'created_at')
    list_filter = ('role', 'is_active', 'department', 'created_at')
    search_fields = ('email', 'first_name', 'last_name', 'phone')
    ordering = ('-created_at',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('المعلومات الشخصية', {'fields': ('first_name', 'last_name', 'phone', 'department')}),
        ('الصلاحيات', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser')}),
        ('تواريخ مهمة', {'fields': ('last_login', 'created_at', 'updated_at')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'first_name', 'last_name', 'phone', 'department', 'role'),
        }),
    )

    readonly_fields = ('created_at', 'updated_at')


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_permissions_count', 'description')
    filter_horizontal = ('permissions',)

    def get_permissions_count(self, obj):
        return obj.permissions.count()

    get_permissions_count.short_description = 'عدد الصلاحيات'


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ('name', 'codename', 'module', 'description')
    list_filter = ('module',)
    search_fields = ('name', 'codename', 'description')


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'model', 'object_id', 'ip_address', 'timestamp')
    list_filter = ('action', 'model', 'timestamp')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'action')
    readonly_fields = ('user', 'action', 'model', 'object_id', 'details', 'ip_address', 'timestamp')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False