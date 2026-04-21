from django.contrib import admin
from .models import *

# إعدادات واجهة الإدارة للتصنيفات: تهدف لتسهيل تنظيم المنتجات في مجموعات منطقية 
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    # الحقول التي تظهر في جدول العرض الرئيسي للتصنيفات
    list_display = ['name', 'parent', 'category_type', 'is_active', 'get_products_count']
    # خيارات التصفية الجانبية لتسريع الوصول لتصنيفات محددة
    list_filter = ['category_type', 'is_active']
    # تفعيل البحث بالاسم لسهولة العثور على التصنيف
    search_fields = ['name']
    # توليد رابط الـ URL (slug) تلقائياً من الاسم أثناء الكتابة (يحسن تجربة المستخدم)
    prepopulated_fields = {'slug': ['name']}


# إعدادات واجهة الإدارة للمنتجات: القلب النابض للمستودع، تتيح إدارة كافة بيانات الأصناف 
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    # عرض البيانات المالية والفنية الأساسية للمنتج في القائمة
    list_display = ['name', 'sku', 'barcode', 'category', 'selling_price', 'is_active']
    # السماح بالفلترة حسب التصنيف أو الحالة (نشط/معطل)
    list_filter = ['category', 'is_active']
    # تفعيل البحث الموسع بالاسم، كود الصنف (SKU)، أو الباركود لسهولة الجرد والبحث
    search_fields = ['name', 'sku', 'barcode']
    # حماية طوابع الوقت من التعديل اليدوي لضمان نزاهة البيانات
    readonly_fields = ['created_at', 'updated_at']
