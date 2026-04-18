from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from warehouse_system import settings
from products.models import Product

class Warehouse(models.Model):
    WAREHOUSE_TYPES = [
        ('main', 'رئيسي'),
        ('branch', 'فرع'),
        ('future', 'مستقبلي'),
    ]

    name = models.CharField(max_length=100, verbose_name="اسم المخزن")
    code = models.CharField(max_length=10, unique=True, verbose_name="كود المخزن")
    warehouse_type = models.CharField(max_length=10, choices=WAREHOUSE_TYPES, default='branch', verbose_name="نوع المخزن")
    address = models.TextField(verbose_name="العنوان")
    manager = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="المدير")
    capacity = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="السعة")
    phone = models.CharField(max_length=20, blank=True, verbose_name="الهاتف")
    is_active = models.BooleanField(default=True, verbose_name="مفعل")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "مخزن"
        verbose_name_plural = "المخازن"

    def __str__(self):
        return self.name

    def get_used_capacity(self):
        total_volume = sum(item.quantity for item in self.inventory_items.all())
        return total_volume


class InventoryItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='inventory_items')
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='inventory_items')
    quantity = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    location = models.CharField(max_length=50, blank=True, verbose_name="الموقع في المخزن")
    expiry_date = models.DateField(null=True, blank=True, verbose_name="تاريخ انتهاء الصلاحية")
    batch_number = models.CharField(max_length=50, blank=True, verbose_name="رقم الدفعة")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "عنصر المخزون"
        verbose_name_plural = "عناصر المخزون"
        unique_together = ['product', 'warehouse', 'batch_number']

    def __str__(self):
        return f"{self.product.name} - {self.warehouse.name}"


class StockMovement(models.Model):
    MOVEMENT_TYPES = [
        ('purchase', 'شراء'),
        ('sale', 'بيع'),
        ('transfer', 'تحويل'),
        ('adjustment', 'تسوية'),
        ('return', 'مرتجع'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    movement_type = models.CharField(max_length=20, choices=MOVEMENT_TYPES)
    quantity = models.IntegerField()
    quantity_before = models.IntegerField()
    quantity_after = models.IntegerField()
    reference_number = models.CharField(max_length=50, blank=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "حركة المخزون"
        verbose_name_plural = "حركات المخزون"
        ordering = ['-created_at']


class StockTransfer(models.Model):
    TRANSFER_STATUS = [
        ('pending', 'معلق'),
        ('in_transit', 'قيد النقل'),
        ('completed', 'مكتمل'),
        ('cancelled', 'ملغي'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    from_warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='transfers_out')
    to_warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='transfers_in')
    quantity = models.IntegerField()
    status = models.CharField(max_length=20, choices=TRANSFER_STATUS, default='pending')
    transfer_date = models.DateTimeField(auto_now_add=True)
    received_date = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "تحويل المخزون"
        verbose_name_plural = "تحويلات المخزون"


class StockAlert(models.Model):
    ALERT_TYPES = [
        ('low_stock', 'مخزون منخفض'),
        ('expiry', 'انتهاء صلاحية'),
        ('excess', 'مخزون زائد'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, null=True, blank=True)
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES)
    message = models.TextField()
    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "تنبيه المخزون"
        verbose_name_plural = "تنبيهات المخزون"
