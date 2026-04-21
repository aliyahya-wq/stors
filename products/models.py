from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator
import uuid
from django.urls import reverse
from django.utils.text import slugify

from warehouse_system import settings

# نموذج التصنيفات: يستخدم لتنظيم المنتجات في مجموعات شجرية (مثل الإلكترونيات -> هواتف)
class Category(models.Model):
    CATEGORY_TYPES = [
        ('electronics', 'الإلكترونيات'),
        ('food', 'الأغذية'),
        ('clothing', 'الملابس'),
        ('home', 'الأدوات المنزلية'),
        ('stationery', 'القرطاسية'),
        ('other', 'أخرى'),
    ]

    name = models.CharField(max_length=100, verbose_name="اسم التصنيف")
    # علاقة self تسمح بإنشاء تصنيفات فرعية داخل تصنيفات رئيسية
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, verbose_name="التصنيف الأب", related_name='children')
    description = models.TextField(blank=True, verbose_name="الوصف")
    # الـ slug يستخدم لتحسين روابط الـ URL (مثل /electronics/ بدل /1/)
    slug = models.SlugField(unique=True, blank=True, null=True)
    image = models.ImageField(upload_to='categories/', null=True, blank=True, verbose_name="صورة")
    category_type = models.CharField(max_length=20, choices=CATEGORY_TYPES, default='other', verbose_name="نوع التصنيف")
    is_active = models.BooleanField(default=True, verbose_name="مفعل")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "تصنيف"
        verbose_name_plural = "التصنيفات"
        ordering = ['name']

    def save(self, *args, **kwargs):  # إعادة تعريف دالة الحفظ لإضافة منطق تلقائي
        # توليد الـ slug تلقائياً من الاسم إذا لم يتم توفيره
        if not self.slug:  # التحقق مما إذا كان حقل الروابط فارغاً
            self.slug = slugify(self.name)  # تحويل الاسم إلى تنسيق يصلح لروابط الويب (Slug)
        super().save(*args, **kwargs)  # استدعاء دالة الحفظ الأصلية لإتمام العملية

    def __str__(self):  # تحديد كيفية تمثيل الكائن كنص (مثلاً في لوحة الإدارة)
        return self.name  # إرجاع اسم التصنيف

    def get_absolute_url(self):
        return reverse('category_detail', kwargs={'pk': self.pk})

    def get_products_count(self):
        # حساب عدد المنتجات المنتمية لهذا التصنيف
        return self.products.count()


# نموذج وحدات القياس: لتعريف وحدات مثل (كجم، قطعة، لتر) والتحويل بينها
class Unit(models.Model):
    name = models.CharField(max_length=50, verbose_name="اسم الوحدة")
    symbol = models.CharField(max_length=10, verbose_name="الرمز")
    # عامل التحويل يستخدم في حال وجود وحدات كبرى وصغرى لنفس الصنف
    conversion_factor = models.DecimalField(max_digits=10, decimal_places=2, default=1.0,
                                            verbose_name="عامل التحويل")
    is_active = models.BooleanField(default=True, verbose_name="مفعل")

    class Meta:
        verbose_name = "وحدة قياس"
        verbose_name_plural = "وحدات القياس"

    def __str__(self):
        return f"{self.name} ({self.symbol})"


# نموذج المنتجات: يمثل الأصناف المخزنة في المستودع بكافة تفاصيلها الفنية والمالية
class Product(models.Model):
    name = models.CharField(max_length=200, verbose_name="اسم المنتج")
    # SKU هو رقم فريد لتعريف الصنف داخل النظام
    sku = models.CharField(max_length=50, unique=True, verbose_name="SKU")
    barcode = models.CharField(max_length=100, unique=True, blank=True, null=True, verbose_name="الباركود")
    description = models.TextField(blank=True, verbose_name="الوصف")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', verbose_name="التصنيف")
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, verbose_name="وحدة القياس")

    # الأسعار: تستخدم في حسابات الفواتير وتقارير الأرباح
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="سعر الشراء")
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="سعر البيع")

    # إعدادات المخزون: لتنبيه المسؤول عند وصول الكمية للحد الحرج (Low Stock)
    min_stock = models.IntegerField(default=0, verbose_name="الحد الأدنى للمخزون")
    max_stock = models.IntegerField(default=0, verbose_name="الحد الأقصى للمخزون")

    # الصور
    main_image = models.ImageField(upload_to='products/main/', null=True, blank=True, verbose_name="الصورة الرئيسية")

    # الحالة: للتحكم في توفر المنتج للعمليات التجارية أو صلاحية استخدامه
    is_active = models.BooleanField(default=True, verbose_name="مفعل")
    has_expiry = models.BooleanField(default=False, verbose_name="له صلاحية")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "منتج"
        verbose_name_plural = "المنتجات"
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # توليد باركود تلقائي فريد للمنتج إذا لم يتم إدخاله يدوياً
        if not self.barcode:
            self.barcode = str(uuid.uuid4())[:13]
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('product_detail', kwargs={'pk': self.pk})

    def get_total_stock(self):
        # حساب إجمالي كمية المنتج المتوفرة في كافة المواقع التخزينية
        return sum(item.quantity for item in self.inventory_items.all())

    def get_stock_status(self):
        # تحديد حالة المخزون بناءً على الحدود الدنيا والقصوى المعرفة
        total_stock = self.get_total_stock()
        if total_stock <= self.min_stock:
            return 'low'
        elif total_stock >= self.max_stock and self.max_stock > 0:
            return 'high'
        else:
            return 'normal'


# نموذج معرض الصور: للسماح بإضافة صور متعددة لنفس المنتج 
class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/gallery/')
    caption = models.CharField(max_length=100, blank=True)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "صورة المنتج"
        verbose_name_plural = "صور المنتج"
