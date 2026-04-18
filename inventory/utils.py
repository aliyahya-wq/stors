import random
import string
from datetime import datetime
from django.utils import timezone


def generate_reference(prefix):
    """إنشاء رقم مرجع فريد"""
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    random_str = ''.join(random.choices(string.digits, k=4))
    return f"{prefix}-{timestamp}-{random_str}"


def check_low_stock():
    """التحقق من المنتجات منخفضة المخزون وإنشاء تنبيهات"""
    from .models import Product, StockAlert

    low_stock_products = Product.objects.annotate(
        total_quantity=Sum('stock_items__quantity')
    ).filter(total_quantity__lte=F('min_stock'))

    for product in low_stock_products:
        # التحقق إذا كان هناك تنبيه نشط بالفعل
        existing_alert = StockAlert.objects.filter(
            product=product,
            is_resolved=False,
            alert_type='low_stock'
        ).exists()

        if not existing_alert:
            StockAlert.objects.create(
                product=product,
                warehouse=None,  # يمكن تحديد مخزن معين لاحقاً
                alert_type='low_stock',
                message=f'المنتج {product.name} وصل للحد الأدنى للمخزون. الكمية الحالية: {product.total_quantity}',
                priority='high'
            )


def calculate_stock_turnover(product, days=30):
    """حساب معدل دوران المخزون"""
    from .models import StockMovement

    end_date = timezone.now()
    start_date = end_date - timezone.timedelta(days=days)

    total_out = StockMovement.objects.filter(
        product=product,
        movement_type='out',
        status='completed',
        created_at__range=[start_date, end_date]
    ).aggregate(total=Sum('quantity'))['total'] or 0

    average_stock = product.total_quantity

    if average_stock > 0:
        return total_out / average_stock
    return 0
