from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from sales.models import SalesInvoice, SalesItem
from purchases.models import PurchaseOrder, PurchaseItem
from inventory.models import InventoryItem
from products.models import Product
from django.db.models import Sum, Count, F
from django.utils import timezone
from datetime import timedelta

@login_required
def dashboard(request):
    total_sales = SalesInvoice.objects.aggregate(t=Sum('total_amount'))['t'] or 0
    total_purchases = PurchaseOrder.objects.aggregate(t=Sum('total_amount'))['t'] or 0
    net_profit = total_sales - total_purchases
    
    total_inventory_items = InventoryItem.objects.aggregate(t=Sum('quantity'))['t'] or 0

    context = {
        'total_sales': total_sales,
        'total_purchases': total_purchases,
        'net_profit': net_profit,
        'total_inventory_items': total_inventory_items,
    }
    return render(request, 'reports/dashboard.html', context)

@login_required
def sales_report(request):
    # مبيعات آخر 30 يوم
    last_30_days = timezone.now() - timedelta(days=30)
    recent_sales = SalesInvoice.objects.filter(created_at__gte=last_30_days)
    
    total_amount = recent_sales.aggregate(t=Sum('total_amount'))['t'] or 0
    total_count = recent_sales.count()
    
    # الأكثر مبيعاً
    top_products = SalesItem.objects.values('product__name').annotate(
        total_qty=Sum('quantity'),
        total_val=Sum('total_price')
    ).order_by('-total_qty')[:10]

    return render(request, 'reports/sales_report.html', {
        'total_amount': total_amount,
        'total_count': total_count,
        'top_products': top_products
    })

@login_required
def purchase_report(request):
    # مشتريات آخر 30 يوم
    last_30_days = timezone.now() - timedelta(days=30)
    recent_purchases = PurchaseOrder.objects.filter(created_at__gte=last_30_days)
    
    total_amount = recent_purchases.aggregate(t=Sum('total_amount'))['t'] or 0
    total_count = recent_purchases.count()
    
    return render(request, 'reports/purchase_report.html', {
        'total_amount': total_amount,
        'total_count': total_count
    })
