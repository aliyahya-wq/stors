from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Sum, Count
from django.http import JsonResponse
from django.core.paginator import Paginator
from .models import *
from .forms import *
from .utils import generate_reference


@login_required
def dashboard(request):
    # إحصائيات سريعة
    total_warehouses = Warehouse.objects.count()
    total_products = Product.objects.count()
    total_stock_value = StockItem.objects.aggregate(
        total_value=Sum(F('quantity') * F('product__cost_price'))
    )['total_value'] or 0

    # التنبيهات النشطة
    active_alerts = StockAlert.objects.filter(is_resolved=False).order_by('-created_at')[:5]

    # الحركات الحديثة
    recent_movements = StockMovement.objects.select_related('product', 'from_warehouse', 'to_warehouse').order_by(
        '-created_at')[:10]

    # المنتجات منخفضة المخزون
    low_stock_products = Product.objects.annotate(
        total_quantity=Sum('stock_items__quantity')
    ).filter(total_quantity__lte=F('min_stock'))[:5]

    context = {
        'total_warehouses': total_warehouses,
        'total_products': total_products,
        'total_stock_value': total_stock_value,
        'active_alerts': active_alerts,
        'recent_movements': recent_movements,
        'low_stock_products': low_stock_products,
    }
    return render(request, 'inventory/dashboard.html', context)


@login_required
def warehouse_list(request):
    warehouses = Warehouse.objects.all().order_by('name')

    # البحث والفلترة
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')

    if search_query:
        warehouses = warehouses.filter(
            Q(name__icontains=search_query) |
            Q(code__icontains=search_query) |
            Q(address__icontains=search_query)
        )

    if status_filter:
        warehouses = warehouses.filter(status=status_filter)

    paginator = Paginator(warehouses, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
    }
    return render(request, 'inventory/warehouse_list.html', context)


@login_required
def warehouse_detail(request, pk):
    warehouse = get_object_or_404(Warehouse, pk=pk)
    stock_items = warehouse.stock_items.select_related('product', 'location')
    recent_movements = StockMovement.objects.filter(
        Q(from_warehouse=warehouse) | Q(to_warehouse=warehouse)
    ).order_by('-created_at')[:10]

    context = {
        'warehouse': warehouse,
        'stock_items': stock_items,
        'recent_movements': recent_movements,
    }
    return render(request, 'inventory/warehouse_detail.html', context)


@login_required
def product_list(request):
    products = Product.objects.select_related('category').all().order_by('name')

    # البحث والفلترة
    search_query = request.GET.get('search', '')
    category_filter = request.GET.get('category', '')
    low_stock_only = request.GET.get('low_stock', '')

    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(sku__icontains=search_query) |
            Q(barcode__icontains=search_query)
        )

    if category_filter:
        products = products.filter(category_id=category_filter)

    if low_stock_only:
        products = products.annotate(
            total_quantity=Sum('stock_items__quantity')
        ).filter(total_quantity__lte=F('min_stock'))

    # إضافة الكمية الإجمالية لكل منتج
    for product in products:
        product.total_qty = product.total_quantity
        product.low_stock = product.low_stock_alert

    categories = Category.objects.all()

    paginator = Paginator(products, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'categories': categories,
        'search_query': search_query,
        'category_filter': category_filter,
        'low_stock_only': low_stock_only,
    }
    return render(request, 'inventory/product_list.html', context)


@login_required
def stock_movements(request):
    movements = StockMovement.objects.select_related(
        'product', 'from_warehouse', 'to_warehouse', 'created_by'
    ).all().order_by('-created_at')

    # البحث والفلترة
    movement_type = request.GET.get('type', '')
    status_filter = request.GET.get('status', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')

    if movement_type:
        movements = movements.filter(movement_type=movement_type)

    if status_filter:
        movements = movements.filter(status=status_filter)

    if date_from:
        movements = movements.filter(created_at__date__gte=date_from)

    if date_to:
        movements = movements.filter(created_at__date__lte=date_to)

    paginator = Paginator(movements, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'movement_type': movement_type,
        'status_filter': status_filter,
        'date_from': date_from,
        'date_to': date_to,
    }
    return render(request, 'inventory/stock_movements.html', context)


@login_required
def create_movement(request):
    if request.method == 'POST':
        form = StockMovementForm(request.POST)
        if form.is_valid():
            movement = form.save(commit=False)
            movement.reference = generate_reference('MOV')
            movement.created_by = request.user

            # معالجة الحركة بناءً على النوع
            if movement.movement_type == 'in' and movement.to_warehouse:
                movement.status = 'completed'
                movement.completed_at = timezone.now()

                # تحديث المخزون
                stock_item, created = StockItem.objects.get_or_create(
                    product=movement.product,
                    warehouse=movement.to_warehouse,
                    defaults={'quantity': movement.quantity}
                )
                if not created:
                    stock_item.quantity += movement.quantity
                    stock_item.save()

            elif movement.movement_type == 'out' and movement.from_warehouse:
                # التحقق من توفر المخزون
                try:
                    stock_item = StockItem.objects.get(
                        product=movement.product,
                        warehouse=movement.from_warehouse
                    )
                    if stock_item.quantity >= movement.quantity:
                        movement.status = 'completed'
                        movement.completed_at = timezone.now()
                        stock_item.quantity -= movement.quantity
                        stock_item.save()
                    else:
                        messages.error(request, 'الكمية غير متوفرة في المخزن')
                        return render(request, 'inventory/movement_create.html', {'form': form})
                except StockItem.DoesNotExist:
                    messages.error(request, 'المنتج غير موجود في المخزن المحدد')
                    return render(request, 'inventory/movement_create.html', {'form': form})

            movement.save()
            messages.success(request, 'تم إنشاء حركة المخزون بنجاح')
            return redirect('stock_movements')
    else:
        form = StockMovementForm()

    context = {'form': form}
    return render(request, 'inventory/movement_create.html', context)


@login_required
def inventory_count_list(request):
    counts = InventoryCount.objects.select_related('warehouse', 'created_by').all().order_by('-created_at')

    status_filter = request.GET.get('status', '')
    if status_filter:
        counts = counts.filter(status=status_filter)

    context = {
        'counts': counts,
        'status_filter': status_filter,
    }
    return render(request, 'inventory/inventory_count.html', context)


@login_required
def create_inventory_count(request):
    if request.method == 'POST':
        form = InventoryCountForm(request.POST)
        if form.is_valid():
            count = form.save(commit=False)
            count.reference = generate_reference('COUNT')
            count.created_by = request.user
            count.save()

            # إنشاء عناصر الجرد
            stock_items = StockItem.objects.filter(warehouse=count.warehouse)
            for stock_item in stock_items:
                CountItem.objects.create(
                    inventory_count=count,
                    stock_item=stock_item,
                    expected_quantity=stock_item.quantity
                )

            messages.success(request, 'تم إنشاء عملية الجرد بنجاح')
            return redirect('inventory_count_detail', pk=count.pk)
    else:
        form = InventoryCountForm()

    context = {'form': form}
    return render(request, 'inventory/count_create.html', context)


@login_required
def inventory_count_detail(request, pk):
    count = get_object_or_404(InventoryCount, pk=pk)
    count_items = count.count_items.select_related('stock_item', 'stock_item__product', 'counted_by')

    if request.method == 'POST' and 'start_count' in request.POST:
        count.status = 'in_progress'
        count.start_date = timezone.now()
        count.save()
        messages.success(request, 'تم بدء عملية الجرد')

    if request.method == 'POST' and 'complete_count' in request.POST:
        count.status = 'completed'
        count.end_date = timezone.now()
        count.save()

        # تحديث كميات المخزون بناءً على الفروقات
        for count_item in count.count_items.filter(actual_quantity__isnull=False):
            if count_item.difference != 0:
                stock_item = count_item.stock_item
                stock_item.quantity = count_item.actual_quantity
                stock_item.save()

        messages.success(request, 'تم إكمال عملية الجرد وتحديث المخزون')

    context = {
        'count': count,
        'count_items': count_items,
    }
    return render(request, 'inventory/count_detail.html', context)


@login_required
def update_count_item(request, pk):
    count_item = get_object_or_404(CountItem, pk=pk)

    if request.method == 'POST':
        form = CountItemForm(request.POST, instance=count_item)
        if form.is_valid():
            count_item = form.save(commit=False)
            count_item.counted_by = request.user
            count_item.counted_at = timezone.now()
            count_item.save()

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'difference': count_item.difference
                })

            messages.success(request, 'تم تحديث الكمية الفعلية')
            return redirect('inventory_count_detail', pk=count_item.inventory_count.pk)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': False})

    return redirect('inventory_count_detail', pk=count_item.inventory_count.pk)


@login_required
def stock_alerts(request):
    alerts = StockAlert.objects.select_related('product', 'warehouse', 'resolved_by').all().order_by('-created_at')

    priority_filter = request.GET.get('priority', '')
    resolved_filter = request.GET.get('resolved', '')

    if priority_filter:
        alerts = alerts.filter(priority=priority_filter)

    if resolved_filter:
        if resolved_filter == 'yes':
            alerts = alerts.filter(is_resolved=True)
        else:
            alerts = alerts.filter(is_resolved=False)

    context = {
        'alerts': alerts,
        'priority_filter': priority_filter,
        'resolved_filter': resolved_filter,
    }
    return render(request, 'inventory/stock_alerts.html', context)


@login_required
def resolve_alert(request, pk):
    alert = get_object_or_404(StockAlert, pk=pk)

    if not alert.is_resolved:
        alert.is_resolved = True
        alert.resolved_by = request.user
        alert.resolved_at = timezone.now()
        alert.save()
        messages.success(request, 'تم حل التنبيه بنجاح')

    return redirect('stock_alerts')


# واجهات API للرسوم البيانية
@login_required
def stock_levels_chart(request):
    products = Product.objects.annotate(total_quantity=Sum('stock_items__quantity'))[:10]

    data = {
        'labels': [product.name for product in products],
        'datasets': [{
            'label': 'الكمية المتاحة',
            'data': [product.total_quantity or 0 for product in products],
            'backgroundColor': '#007bff',
        }]
    }

    return JsonResponse(data)


@login_required
def movement_stats_chart(request):
    from django.db.models.functions import TruncMonth

    movements = StockMovement.objects.filter(
        status='completed',
        created_at__gte=timezone.now() - timezone.timedelta(days=365)
    ).annotate(month=TruncMonth('created_at')).values('month', 'movement_type').annotate(
        count=Count('id')
    ).order_by('month')

    # معالجة البيانات للرسم البياني
    # ... (كود معالجة البيانات)

    return JsonResponse(movement_data)
