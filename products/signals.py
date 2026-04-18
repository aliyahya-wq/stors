from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Product
from inventory.models import StockMovement, StockAlert
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Product)
def create_product_barcode(sender, instance, created, **kwargs):
    """
    إنشاء باركود تلقائي للمنتج عند الإنشاء
    """
    if created and not instance.barcode:
        # في التطبيق الحقيقي، يمكن استخدام مكتبة لتوليد الباركود
        instance.barcode = f"PROD{instance.id:08d}"
        instance.save(update_fields=['barcode'])
        logger.info(f'تم إنشاء باركود للمنتج: {instance.name}')


@receiver(post_save, sender=StockMovement)
def check_stock_after_movement(sender, instance, created, **kwargs):
    """
    التحقق من مستوى المخزون بعد كل حركة
    """
    if created:
        product = instance.product
        total_stock = product.get_total_stock()

        # التحقق من المخزون المنخفض
        if total_stock <= product.min_stock:
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

        # التحقق من المخزون المرتفع
        elif product.max_stock > 0 and total_stock >= product.max_stock:
            if not StockAlert.objects.filter(
                    product=product,
                    alert_type='excess',
                    is_resolved=False
            ).exists():
                StockAlert.objects.create(
                    product=product,
                    alert_type='excess',
                    message=f'المخزون مرتفع للمنتج {product.name}. المخزون الحالي: {total_stock}'
                )


@receiver(pre_save, sender=Product)
def validate_product_prices(sender, instance, **kwargs):
    """
    التحقق من أن سعر البيع أكبر من سعر الشراء
    """
    if instance.selling_price <= instance.purchase_price:
        raise ValidationError('سعر البيع يجب أن يكون أكبر من سعر الشراء')
