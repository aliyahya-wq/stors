class InventoryTracker:
    """
    فئة لتتبع وإدارة المخزون
    """

    def __init__(self):
        self.low_stock_threshold = 0.1  # 10%
        self.high_stock_threshold = 0.9  # 90%

    def get_stock_level(self, product, warehouse=None):
        """
        الحصول على مستوى المخزون لمنتج معين
        """
        total_stock = product.get_total_stock()
        max_stock = product.max_stock

        if max_stock == 0:
            return 'unknown'

        stock_ratio = total_stock / max_stock

        if stock_ratio <= self.low_stock_threshold:
            return 'low'
        elif stock_ratio >= self.high_stock_threshold:
            return 'high'
        else:
            return 'normal'

    def get_reorder_recommendation(self, product):
        """
        الحصول على توصية إعادة الطلب
        """
        current_stock = product.get_total_stock()
        min_stock = product.min_stock
        max_stock = product.max_stock

        if max_stock == 0:
            return "غير محدد"

        if current_stock <= min_stock:
            reorder_quantity = max_stock - current_stock
            return f"إعادة طلب {reorder_quantity} {product.unit.symbol}"
        else:
            return "لا حاجة لإعادة الطلب"

    def get_inventory_turnover(self, product, days=30):
        """
        حساب معدل دوران المخزون
        """
        from django.utils import timezone
        from django.db.models import Sum
        from inventory.models import StockMovement

        start_date = timezone.now() - timezone.timedelta(days=days)

        # مجموع المبيعات خلال الفترة
        sales = StockMovement.objects.filter(
            product=product,
            movement_type='sale',
            created_at__gte=start_date
        ).aggregate(total=Sum('quantity'))['total'] or 0

        # متوسط المخزون
        avg_stock = product.get_total_stock()

        if avg_stock > 0:
            turnover = sales / avg_stock
            return round(turnover, 2)
        else:
            return 0

    def get_slow_moving_products(self, days=90, threshold=0.1):
        """
        الحصول على المنتجات بطيئة الحركة
        """
        from .models import Product

        slow_products = []
        for product in Product.objects.all():
            turnover = self.get_inventory_turnover(product, days)
            if turnover < threshold:
                slow_products.append({
                    'product': product,
                    'turnover': turnover,
                    'current_stock': product.get_total_stock()
                })

        return sorted(slow_products, key=lambda x: x['turnover'])

    def generate_inventory_report(self):
        """
        توليد تقرير شامل عن المخزون
        """
        from .models import Product

        report = {
            'total_products': Product.objects.count(),
            'active_products': Product.objects.filter(is_active=True).count(),
            'low_stock_products': [],
            'high_stock_products': [],
            'out_of_stock_products': [],
            'slow_moving_products': self.get_slow_moving_products()
        }

        for product in Product.objects.all():
            stock_level = self.get_stock_level(product)
            total_stock = product.get_total_stock()

            if stock_level == 'low':
                report['low_stock_products'].append({
                    'product': product,
                    'current_stock': total_stock,
                    'min_stock': product.min_stock
                })
            elif stock_level == 'high':
                report['high_stock_products'].append({
                    'product': product,
                    'current_stock': total_stock,
                    'max_stock': product.max_stock
                })

            if total_stock == 0:
                report['out_of_stock_products'].append(product)

        return report
