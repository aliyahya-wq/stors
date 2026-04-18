from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from sales.models import SalesInvoice
from purchases.models import PurchaseOrder
from inventory.models import InventoryItem
from django.db.models import Sum

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
