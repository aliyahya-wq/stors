from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, UserRole, Permission, ActivityLog

# إعداد واجهة الإدارة الافتراضية لجانغو (Admin Interface) لتسهيل إدارة البيانات من قبل المطورين

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    # الحقول التي تظهر في جدول عرض المستخدمين
    list_display = ('email', 'first_name', 'last_name', 'role', 'department', 'is_active', 'created_at')  # تحديد الأعمدة الظاهرة في القائمة الرئيسية
    
    # خيارات التصفية الجانبية في لوحة الإدارة
    list_filter = ('role', 'is_active', 'department', 'created_at')  # إضافة فلاتر لتسهيل الوصول للمجموعات المعينة
    
    # حقول البحث في قاعدة بيانات المستخدمين
    search_fields = ('email', 'first_name', 'last_name', 'phone')  # تفعيل محرك البحث لهذه الحقول النصية
    
    # ترتيب العرض (الأحدث أولاً)
    ordering = ('-created_at',)  # ضبط الترتيب الافتراضي ليكون تنازلياً حسب تاريخ الإنشاء

    # تقسيم حقول الإدخال في صفحة تعديل المستخدم إلى مجموعات منطقية
    fieldsets = (
        (None, {'fields': ('email', 'password')}),  # مجموعة البيانات الأساسية لتسجيل الدخول
        ('المعلومات الشخصية', {'fields': ('first_name', 'last_name', 'phone', 'department')}),  # مجموعة بيانات التواصل
        ('الصلاحيات', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser')}),  # مجموعة التحكم في الأذونات
        ('تواريخ مهمة', {'fields': ('last_login', 'created_at', 'updated_at')}),  # مجموعة التتبع الزمني
    )

    # الحقول المطلوبة عند إنشاء مستخدم جديد من لوحة الإدارة
    add_fieldsets = (
        (None, {
            'classes': ('wide',),  # تطبيق فئة CSS لجعل النموذج عريضاً ومنسقاً
            'fields': ('email', 'password1', 'password2', 'first_name', 'last_name', 'phone', 'department', 'role'),  # الحقول اللازمة للإنشاء الأولي
        }),
    )

    # حقول للقراءة فقط (Read-only) لمنع التعديل اليدوي على تواريخ النظام التلقائية
    readonly_fields = ('created_at', 'updated_at')  # حماية حقول التوقيت التلقائي من التغيير اليدوي


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    # عرض اسم الدور وعدد الصلاحيات الممنوحة له
    list_display = ('name', 'get_permissions_count', 'description')  # عرض الدور وعدد صلاحياته لسهولة المراجعة
    
    # أداة اختيار الصلاحيات بشكل أفقي مرن (Horizontal Filter)
    filter_horizontal = ('permissions',)  # تحسين واجهة اختيار الصلاحيات لتكون بنظام القائمتين المتقابلتين

    def get_permissions_count(self, obj):
        # حساب عدد الصلاحيات المرتبطة بهذا الدور
        return obj.permissions.count()  # تنفيذ استعلام لحساب عدد العناصر في علاقة Many-to-Many

    get_permissions_count.short_description = 'عدد الصلاحيات'  # تحديد العنوان الذي سيظهر في رأس الجدول لهذا العمود


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    # عرض الصلاحيات المتاحة في النظام مع تصنيفها حسب الوحدة البرمجية
    list_display = ('name', 'codename', 'module', 'description')  # عرض البيانات التقنية والوصفية للصلاحية
    list_filter = ('module',)  # السماح بتصفية الصلاحيات حسب الوحدة (مخازن، مبيعات، إلخ)
    search_fields = ('name', 'codename', 'description')  # تفعيل البحث للوصول السريع للصلاحيات البرمجية


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    # عرض سجل الأنشطة للمراقبة الأمنية والإدارية
    list_display = ('user', 'action', 'model', 'object_id', 'ip_address', 'timestamp')  # تتبع من قام وبماذا ومتى وأين
    list_filter = ('action', 'model', 'timestamp')  # تصفية السجلات لملاحقة عمليات معينة في وقت محدد
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'action')  # البحث عن أنشطة مستخدم معين
    
    # جعل جميع حقول السجل للقراءة فقط لمنع تلاعب المسؤولين بالسجلات التاريخية
    readonly_fields = ('user', 'action', 'model', 'object_id', 'details', 'ip_address', 'timestamp')  # منع أي تعديل لضمان نزاهة المراجعة (Audit)

    def has_add_permission(self, request):
        # منع إضافة سجلات يدوياً (السجلات تولد تلقائياً فقط)
        return False  # إرجاع False لتعطيل زر "إضافة" في لوحة الإدارة لهذا النموذج

    def has_change_permission(self, request, obj=None):
        # منع تعديل السجلات الموجودة لضمان نزاهة البيانات
        return False  # إرجاع False لتعطيل إمكانية حفظ أي تغييرات على السجلات القديمة
