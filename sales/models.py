from django.db import models
from django.conf import settings
from products.models import Product
from inventory.models import Warehouse

class Customer(models.Model):
    name = models.CharField(max_length=200, verbose_name="اسم العميل")
    phone = models.CharField(max_length=20, verbose_name="رقم الهاتف")
    email = models.EmailField(blank=True, verbose_name="البريد الإلكتروني")
    address = models.TextField(blank=True, verbose_name="العنوان")
    is_active = models.BooleanField(default=True, verbose_name="مفعل")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "عميل"
        verbose_name_plural = "العملاء"
        ordering = ['-created_at']

    def __str__(self):
        return self.name

class SalesInvoice(models.Model):
    STATUS_CHOICES = [
        ('pending', 'قيد الانتظار'),
        ('paid', 'مدفوعة'),
        ('cancelled', 'ملغاة'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, verbose_name="العميل", null=True, blank=True)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, verbose_name="المخزن المصدر")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name="البائع")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='paid', verbose_name="حالة الفاتورة")
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="إجمالي القيمة")
    notes = models.TextField(blank=True, verbose_name="ملاحظات")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")

    class Meta:
        verbose_name = "فاتورة مبيعات"
        verbose_name_plural = "فواتير المبيعات"
        ordering = ['-created_at']

    def __str__(self):
        return f"INV-{self.id} / {self.customer.name if self.customer else 'عميل نقدي'}"

class SalesItem(models.Model):
    invoice = models.ForeignKey(SalesInvoice, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="المنتج")
    quantity = models.IntegerField(verbose_name="الكمية")
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="سعر الوحدة")
    total_price = models.DecimalField(max_digits=12, decimal_places=2, editable=False, verbose_name="الإجمالي")

    class Meta:
        verbose_name = "عنصر مبيعات"
        verbose_name_plural = "عناصر المبيعات"

    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} ({self.quantity})"
