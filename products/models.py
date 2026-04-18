from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator
import uuid
from django.urls import reverse
from django.utils.text import slugify

from warehouse_system import settings


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
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, verbose_name="التصنيف الأب")
    description = models.TextField(blank=True, verbose_name="الوصف")
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

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('category_detail', kwargs={'pk': self.pk})

    def get_products_count(self):
        return self.products.count()


class Unit(models.Model):
    name = models.CharField(max_length=50, verbose_name="اسم الوحدة")
    symbol = models.CharField(max_length=10, verbose_name="الرمز")
    conversion_factor = models.DecimalField(max_digits=10, decimal_places=2, default=1.0,
                                            verbose_name="عامل التحويل")
    is_active = models.BooleanField(default=True, verbose_name="مفعل")

    class Meta:
        verbose_name = "وحدة قياس"
        verbose_name_plural = "وحدات القياس"

    def __str__(self):
        return f"{self.name} ({self.symbol})"


class Product(models.Model):
    name = models.CharField(max_length=200, verbose_name="اسم المنتج")
    sku = models.CharField(max_length=50, unique=True, verbose_name="SKU")
    barcode = models.CharField(max_length=100, unique=True, blank=True, null=True, verbose_name="الباركود")
    description = models.TextField(blank=True, verbose_name="الوصف")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', verbose_name="التصنيف")
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, verbose_name="وحدة القياس")

    # الأسعار
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="سعر الشراء")
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="سعر البيع")

    # إعدادات المخزون
    min_stock = models.IntegerField(default=0, verbose_name="الحد الأدنى للمخزون")
    max_stock = models.IntegerField(default=0, verbose_name="الحد الأقصى للمخزون")

    # الصور
    main_image = models.ImageField(upload_to='products/main/', null=True, blank=True, verbose_name="الصورة الرئيسية")

    # الحالة
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
        if not self.barcode:
            self.barcode = str(uuid.uuid4())[:13]
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('product_detail', kwargs={'pk': self.pk})

    def get_total_stock(self):
        return sum(item.quantity for item in self.inventory_items.all())

    def get_stock_status(self):
        total_stock = self.get_total_stock()
        if total_stock <= self.min_stock:
            return 'low'
        elif total_stock >= self.max_stock and self.max_stock > 0:
            return 'high'
        else:
            return 'normal'


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/gallery/')
    caption = models.CharField(max_length=100, blank=True)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "صورة المنتج"
        verbose_name_plural = "صور المنتج"


