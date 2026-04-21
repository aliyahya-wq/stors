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
    if created and not instance.barcode:  # التحقق من أن الكائن جديد كلياً ولا يملك باركود
        # في التطبيق الحقيقي، يمكن استخدام مكتبة لتوليد الباركود
        instance.barcode = f"PROD{instance.id:08d}"  # توليد رقم تسلسلي فريد يعتمد على معرف المنتج في قاعدة البيانات
        instance.save(update_fields=['barcode'])  # حفظ حقل الباركود فقط لتجنب إعادة تفعيل إشارات الحفظ الأخرى
        logger.info(f'تم إنشاء باركود للمنتج: {instance.name}')  # تسجيل العملية في ملفات السجل (Logs) للسيستم


@receiver(post_save, sender=StockMovement)
def check_stock_after_movement(sender, instance, created, **kwargs):
    """
    التحقق من مستوى المخزون بعد كل حركة
    """
    if created:  # التأكد من أن الحركة المخزنية تم تسجيلها بنجاح
        product = instance.product  # الوصول للمنتج المتأثر بالحركة
        total_stock = product.get_total_stock()  # استدعاء دالة حساب الإجمالي الفعلي في كافة المخازن

        # التحقق من المخزون المنخفض
        if total_stock <= product.min_stock:  # إذا وصلت الكمية للحد الأدنى أو أقل
            if not StockAlert.objects.filter(  # التأكد من عدم وجود تنبيه نشط لنفس السبب لتجنب التكرار المزعج
                    product=product,
                    alert_type='low_stock',
                    is_resolved=False
            ).exists():
                StockAlert.objects.create(  # إنشاء تنبيه رسمي ليظهر في لوحة التحكم للمسؤول
                    product=product,
                    alert_type='low_stock',
                    message=f'المخزون منخفض للمنتج {product.name}. المخزون الحالي: {total_stock}'
                )

        # التحقق من المخزون المرتفع
        elif product.max_stock > 0 and total_stock >= product.max_stock:  # التحقق من تجاوز السعة القصوى المحددة
            if not StockAlert.objects.filter(  # فحص وجود تنبيهات سابقة لم تحل
                    product=product,
                    alert_type='excess',
                    is_resolved=False
            ).exists():
                StockAlert.objects.create(  # تسجيل تنبيه فائض مخزوني للرقابة المالية والإدارية
                    product=product,
                    alert_type='excess',
                    message=f'المخزون مرتفع للمنتج {product.name}. المخزون الحالي: {total_stock}'
                )


@receiver(pre_save, sender=Product)
def validate_product_prices(sender, instance, **kwargs):
    """
    التحقق من أن سعر البيع أكبر من سعر الشراء
    """
    if instance.selling_price <= instance.purchase_price:  # قاعدة برمجية لمنع البيع بخسارة أو بسعر التكلفة
        raise ValidationError('سعر البيع يجب أن يكون أكبر من سعر الشراء')  # منع حفظ البيانات في قاعدة البيانات وإرجاع خطأ
