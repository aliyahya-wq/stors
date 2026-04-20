import pandas as pd
from django.core.exceptions import ValidationError
from .models import Product, Category, Unit
import os
from datetime import datetime


def import_products_from_excel(file_path):
    """
    استيراد المنتجات من ملف Excel
    """
    try:
        df = pd.read_excel(file_path)
        results = {
            'success': 0,
            'errors': [],
            'total': len(df)
        }

        for index, row in df.iterrows():
            try:
                # التحقق من البيانات المطلوبة
                if pd.isna(row['name']) or pd.isna(row['sku']):
                    results['errors'].append(f"الصف {index + 2}: الاسم و SKU مطلوبان")
                    continue

                # التحقق من عدم تكرار SKU
                if Product.objects.filter(sku=row['sku']).exists():
                    results['errors'].append(f"الصف {index + 2}: SKU مكرر - {row['sku']}")
                    continue

                # الحصول على التصنيف
                try:
                    category = Category.objects.get(name=row['category'])
                except Category.DoesNotExist:
                    results['errors'].append(f"الصف {index + 2}: التصنيف غير موجود - {row['category']}")
                    continue

                # الحصول على وحدة القياس
                try:  # محاولة مطابقة وحدة القياس
                    unit = Unit.objects.get(name=row['unit'])  # البحث عن الوحدة بالاسم
                except Unit.DoesNotExist:  # إذا كانت الوحدة غير معرفة مسبقاً في النظام
                    results['errors'].append(f"الصف {index + 2}: وحدة القياس غير موجودة - {row['unit']}")
                    continue

                # إنشاء المنتج
                product = Product(  # بناء كائن المنتج وتعيين القيم من أعمدة صف الإكسل
                    name=row['name'],
                    sku=row['sku'],
                    category=category,
                    unit=unit,
                    description=row.get('description', ''),  # استخدام .get لتفادي الأخطاء في حال غياب العمود
                    purchase_price=row.get('purchase_price', 0),
                    selling_price=row.get('selling_price', 0),
                    min_stock=row.get('min_stock', 0),
                    max_stock=row.get('max_stock', 0),
                    is_active=row.get('is_active', True)
                )

                product.save()  # حفظ المنتج فعلياً في قاعدة البيانات
                results['success'] += 1  # زيادة عداد النجاح

            except Exception as e:  # التقاط أي خطأ غير متوقع أثناء معالجة صف معين
                results['errors'].append(f"الصف {index + 2}: {str(e)}")  # تدوين الخطأ لمراجعته من قبل المستخدم

        return results  # إرجاع التقرير النهائي لعملية الاستيراد

    except Exception as e:
        return {
            'success': 0,
            'errors': [f"خطأ في قراءة الملف: {str(e)}"],
            'total': 0
        }


def export_products_to_excel(queryset, file_path):
    """
    تصدير المنتجات إلى ملف Excel
    """
    data = []
    for product in queryset:
        data.append({
            'الاسم': product.name,
            'SKU': product.sku,
            'الباركود': product.barcode,
            'التصنيف': product.category.name,
            'وحدة القياس': product.unit.name,
            'سعر الشراء': product.purchase_price,
            'سعر البيع': product.selling_price,
            'الحد الأدنى': product.min_stock,
            'الحد الأقصى': product.max_stock,
            'المخزون الإجمالي': product.get_total_stock(),
            'الحالة': 'نشط' if product.is_active else 'معطل',
            'تاريخ الإضافة': product.created_at.strftime('%Y-%m-%d')
        })

    df = pd.DataFrame(data)
    df.to_excel(file_path, index=False, engine='openpyxl')

    return file_path


def generate_barcode(sku):
    """
    توليد باركود للمنتج (تنفيذ مبسط)
    في التطبيق الحقيقي، يمكن استخدام مكتبة مثل python-barcode
    """
    return f"BC{sku}123456"


def check_low_stock_alerts():
    """
    التحقق من المنتجات منخفضة المخزون وإنشاء تنبيهات
    """
    from inventory.models import StockAlert
    from .models import Product

    low_stock_products = []
    for product in Product.objects.all():
        total_stock = product.get_total_stock()
        if total_stock <= product.min_stock:
            low_stock_products.append(product)

            # التحقق من عدم وجود تنبيه مفتوح لنفس المنتج
            if not StockAlert.objects.filter(
                    product=product,
                    alert_type='low_stock',
                    is_resolved=False
            ).exists():
                StockAlert.objects.create(
                    product=product,
                    alert_type='low_stock',
                    message=f'المخزون منخفض للمنتج {product.name}. المخزون الحالي: {total_stock}'
                )

    return low_stock_products


def get_inventory_stats():
    """
    الحصول على إحصائيات المخزون
    """
    from inventory.models import StockMovement
    from .models import Product

    total_products = Product.objects.count()
    active_products = Product.objects.filter(is_active=True).count()

    # حركات اليوم
    today = datetime.now().date()
    today_movements = StockMovement.objects.filter(created_at__date=today).count()

    # المنتجات منخفضة المخزون
    low_stock_count = 0
    for product in Product.objects.all():
        if product.get_total_stock() <= product.min_stock:
            low_stock_count += 1

    return {
        'total_products': total_products,
        'active_products': active_products,
        'today_movements': today_movements,
        'low_stock_count': low_stock_count
    }
