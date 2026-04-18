from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Sum, Count
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from .models import *
from inventory.models import Warehouse, InventoryItem, StockMovement, StockTransfer, StockAlert
from .forms import *
import pandas as pd
import os
import time
from datetime import datetime
from .utils import import_products_from_excel, export_products_to_excel
from sales.models import SalesInvoice, Customer
from purchases.models import PurchaseOrder, Supplier



@login_required

def dashboard(request):
    # إحصائيات المخزون
    total_products = Product.objects.count()
    total_categories = Category.objects.count()
    total_warehouses = Warehouse.objects.count()
    low_stock_alerts = StockAlert.objects.filter(is_resolved=False, alert_type='low_stock').count()

    # إحصائيات المبيعات والمشتريات والشركاء
    total_sales = SalesInvoice.objects.aggregate(t=Sum('total_amount'))['t'] or 0
    total_purchases = PurchaseOrder.objects.aggregate(t=Sum('total_amount'))['t'] or 0
    total_customers = Customer.objects.count()
    total_suppliers = Supplier.objects.count()

    # المنتجات منخفضة المخزون
    low_stock_products = []
    for product in Product.objects.all():
        total_stock = product.get_total_stock()
        if total_stock <= product.min_stock:
            low_stock_products.append({
                'product': product,
                'current_stock': total_stock,
                'min_stock': product.min_stock
            })

    # حركات المخزون الحديثة
    recent_movements = StockMovement.objects.select_related('product', 'warehouse').order_by('-created_at')[:10]
    
    # قائمة المخازن للرسوم البيانية أو التقارير
    warehouses = Warehouse.objects.all()

    context = {
        'total_products': total_products,
        'total_categories': total_categories,
        'total_warehouses': total_warehouses,
        'low_stock_alerts': low_stock_alerts,
        'total_sales': total_sales,
        'total_purchases': total_purchases,
        'total_customers': total_customers,
        'total_suppliers': total_suppliers,
        'low_stock_products': low_stock_products[:5],
        'recent_movements': recent_movements,
        'warehouses': warehouses,
    }
    return render(request, 'products/inventory/dashboard.html', context)


@login_required

def category_list(request):
    categories = Category.objects.filter(parent__isnull=True).prefetch_related('products')
    return render(request, 'products/categories/list.html', {'categories': categories})


@login_required

def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            category = form.save()
            messages.success(request, 'تم إنشاء التصنيف بنجاح')
            return redirect('category_list')
    else:
        form = CategoryForm()
    return render(request, 'products/categories/create.html', {'form': form})


@login_required

def category_detail(request, pk):
    category = get_object_or_404(Category, pk=pk)
    products = category.products.all()
    subcategories = Category.objects.filter(parent=category)

    context = {
        'category': category,
        'products': products,
        'subcategories': subcategories,
    }
    return render(request, 'products/categories/detail.html', context)


@login_required

def product_list(request):
    products = Product.objects.select_related('category', 'unit').prefetch_related('inventory_items')

    # البحث
    search_query = request.GET.get('search', '')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(sku__icontains=search_query) |
            Q(barcode__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    # الفلترة
    category_filter = request.GET.get('category', '')
    if category_filter:
        products = products.filter(category_id=category_filter)

    warehouse_filter = request.GET.get('warehouse', '')
    if warehouse_filter:
        products = products.filter(inventory_items__warehouse_id=warehouse_filter)

    stock_status = request.GET.get('stock_status', '')
    if stock_status:
        product_ids = []
        for product in products:
            if product.get_stock_status() == stock_status:
                product_ids.append(product.id)
        products = products.filter(id__in=product_ids)

    # التصنيف
    sort_by = request.GET.get('sort', 'name')
    if sort_by in ['name', 'sku', 'selling_price', 'created_at']:
        products = products.order_by(sort_by)

    # الترقيم
    paginator = Paginator(products, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    categories = Category.objects.all()
    warehouses = Warehouse.objects.all()

    context = {
        'page_obj': page_obj,
        'categories': categories,
        'warehouses': warehouses,
        'search_query': search_query,
        'filters': {
            'category': category_filter,
            'warehouse': warehouse_filter,
            'stock_status': stock_status,
            'sort': sort_by,
        }
    }
    return render(request, 'products/products/list.html', context)


@login_required

def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            messages.success(request, 'تم إنشاء المنتج بنجاح')
            return redirect('product_detail', pk=product.pk)
    else:
        # توليد SKU تلقائي
        last_product = Product.objects.order_by('-id').first()
        next_sku = f"PROD{last_product.id + 1:06d}" if last_product else "PROD000001"
        form = ProductForm(initial={'sku': next_sku})

    return render(request, 'products/products/create.html', {'form': form})


@login_required

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    inventory_items = product.inventory_items.select_related('warehouse')
    movements = StockMovement.objects.filter(product=product).order_by('-created_at')[:20]

    context = {
        'product': product,
        'inventory_items': inventory_items,
        'movements': movements,
    }
    return render(request, 'products/products/detail.html', context)


@login_required

def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تحديث المنتج بنجاح')
            return redirect('product_detail', pk=product.pk)
    else:
        form = ProductForm(instance=product)

    return render(request, 'products/products/update.html', {'form': form, 'product': product})


@login_required

def warehouse_list(request):
    warehouses = Warehouse.objects.select_related('manager').prefetch_related('inventory_items')
    return render(request, 'products/warehouses/list.html', {'warehouses': warehouses})


@login_required

def warehouse_detail(request, pk):
    warehouse = get_object_or_404(Warehouse, pk=pk)
    inventory_items = warehouse.inventory_items.select_related('product').order_by('product__name')

    # إحصائيات المخزون
    total_products = inventory_items.count()
    total_quantity = inventory_items.aggregate(total=Sum('quantity'))['total'] or 0
    low_stock_items = [item for item in inventory_items if item.quantity <= item.product.min_stock]

    context = {
        'warehouse': warehouse,
        'inventory_items': inventory_items,
        'total_products': total_products,
        'total_quantity': total_quantity,
        'low_stock_items': low_stock_items,
    }
    return render(request, 'products/warehouses/detail.html', context)


@login_required

def stock_movements(request):
    movements = StockMovement.objects.select_related('product', 'warehouse', 'created_by').order_by('-created_at')

    # الفلترة
    movement_type = request.GET.get('type', '')
    if movement_type:
        movements = movements.filter(movement_type=movement_type)

    product_filter = request.GET.get('product', '')
    if product_filter:
        movements = movements.filter(product_id=product_filter)

    warehouse_filter = request.GET.get('warehouse', '')
    if warehouse_filter:
        movements = movements.filter(warehouse_id=warehouse_filter)

    # الترقيم
    paginator = Paginator(movements, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    products = Product.objects.all()
    warehouses = Warehouse.objects.all()

    context = {
        'page_obj': page_obj,
        'products': products,
        'warehouses': warehouses,
        'filters': {
            'type': movement_type,
            'product': product_filter,
            'warehouse': warehouse_filter,
        }
    }
    return render(request, 'products/inventory/movements.html', context)


@login_required

def stock_adjustment(request):
    if request.method == 'POST':
        form = InventoryAdjustmentForm(request.POST)
        if form.is_valid():
            adjustment = form.save(commit=False)
            adjustment.movement_type = 'adjustment'
            adjustment.created_by = request.user

            # الحصول على المخزون الحالي
            inventory_item, created = InventoryItem.objects.get_or_create(
                product=adjustment.product,
                warehouse=adjustment.warehouse,
                defaults={'quantity': 0}
            )

            adjustment.quantity_before = inventory_item.quantity
            adjustment.quantity_after = adjustment.quantity
            inventory_item.quantity = adjustment.quantity
            inventory_item.save()

            adjustment.save()
            messages.success(request, 'تم تسوية المخزون بنجاح')
            return redirect('stock_movements')
    else:
        form = InventoryAdjustmentForm()

    return render(request, 'products/inventory/adjustment.html', {'form': form})


@login_required

def stock_transfer(request):
    if request.method == 'POST':
        form = StockTransferForm(request.POST)
        if form.is_valid():
            transfer = form.save(commit=False)
            transfer.created_by = request.user

            # التحقق من توفر المخزون في المخزن المصدر
            from_inventory = InventoryItem.objects.filter(
                product=transfer.product,
                warehouse=transfer.from_warehouse
            ).first()

            if not from_inventory or from_inventory.quantity < transfer.quantity:
                messages.error(request, 'لا يوجد مخزون كافي في المخزن المصدر')
            else:
                # خصم من المخزن المصدر
                from_inventory.quantity -= transfer.quantity
                from_inventory.save()

                # إضافة إلى المخزن الهدف
                to_inventory, created = InventoryItem.objects.get_or_create(
                    product=transfer.product,
                    warehouse=transfer.to_warehouse,
                    defaults={'quantity': 0}
                )
                to_inventory.quantity += transfer.quantity
                to_inventory.save()

                # تسجيل الحركة
                StockMovement.objects.create(
                    product=transfer.product,
                    warehouse=transfer.from_warehouse,
                    movement_type='transfer_out',
                    quantity=-transfer.quantity,
                    quantity_before=from_inventory.quantity + transfer.quantity,
                    quantity_after=from_inventory.quantity,
                    reference_number=f"TRF-{transfer.id}",
                    notes=transfer.notes,
                    created_by=request.user
                )

                StockMovement.objects.create(
                    product=transfer.product,
                    warehouse=transfer.to_warehouse,
                    movement_type='transfer_in',
                    quantity=transfer.quantity,
                    quantity_before=to_inventory.quantity - transfer.quantity,
                    quantity_after=to_inventory.quantity,
                    reference_number=f"TRF-{transfer.id}",
                    notes=transfer.notes,
                    created_by=request.user
                )

                transfer.save()
                messages.success(request, 'تم تحويل المخزون بنجاح')
                return redirect('stock_transfers')
    else:
        form = StockTransferForm()

    return render(request, 'products/inventory/transfers.html', {'form': form})


@login_required

def stock_alerts(request):
    alerts = StockAlert.objects.select_related('product', 'warehouse').filter(is_resolved=False).order_by('-created_at')
    return render(request, 'products/inventory/stock_alerts.html', {'alerts': alerts})


@login_required

def barcode_generator(request):
    products = Product.objects.all()
    return render(request, 'products/barcode/generator.html', {'products': products})


@login_required

def barcode_scanner(request):
    return render(request, 'products/barcode/scanner.html')


@login_required

def search_by_barcode(request):
    barcode = request.GET.get('barcode', '')
    if barcode:
        try:
            product = Product.objects.get(barcode=barcode)
            return JsonResponse({
                'success': True,
                'product': {
                    'id': product.id,
                    'name': product.name,
                    'sku': product.sku,
                    'barcode': product.barcode,
                    'selling_price': str(product.selling_price),
                    'main_image': product.main_image.url if product.main_image else '',
                }
            })
        except Product.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'المنتج غير موجود'})

    return JsonResponse({'success': False, 'message': 'لم يتم إدخال باركود'})


@login_required

def product_search(request):
    """
    بحث متقدم في المنتجات
    """
    products = Product.objects.select_related('category', 'unit').prefetch_related('inventory_items')

    # البحث النصي
    search_query = request.GET.get('q', '')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(sku__icontains=search_query) |
            Q(barcode__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    # الفلترة
    category_filter = request.GET.get('category', '')
    if category_filter:
        products = products.filter(category_id=category_filter)

    warehouse_filter = request.GET.get('warehouse', '')
    if warehouse_filter:
        products = products.filter(inventory_items__warehouse_id=warehouse_filter)

    stock_status = request.GET.get('stock_status', '')
    if stock_status:
        product_ids = []
        for product in products:
            if stock_status == 'low' and product.get_stock_status() == 'low':
                product_ids.append(product.id)
            elif stock_status == 'normal' and product.get_stock_status() == 'normal':
                product_ids.append(product.id)
            elif stock_status == 'high' and product.get_stock_status() == 'high':
                product_ids.append(product.id)
            elif stock_status == 'out' and product.get_total_stock() == 0:
                product_ids.append(product.id)
        products = products.filter(id__in=product_ids)

    # نطاق السعر
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    if min_price:
        products = products.filter(selling_price__gte=min_price)
    if max_price:
        products = products.filter(selling_price__lte=max_price)

    # حالة المنتج
    is_active = request.GET.get('is_active', '')
    if is_active == 'true':
        products = products.filter(is_active=True)
    elif is_active == 'false':
        products = products.filter(is_active=False)

    # الترتيب
    sort_by = request.GET.get('sort', 'name')
    if sort_by in ['name', 'sku', 'selling_price', '-selling_price', 'created_at', '-created_at']:
        products = products.order_by(sort_by)

    # الترقيم
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    categories = Category.objects.all()
    warehouses = Warehouse.objects.all()

    context = {
        'products': page_obj,
        'categories': categories,
        'warehouses': warehouses,
        'search_query': search_query,
    }
    return render(request, 'products/products/search.html', context)


@login_required

def bulk_import(request):
    """
    الاستيراد الجماعي للمنتجات
    """
    if request.method == 'POST':
        form = BulkImportForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = request.FILES['excel_file']

            # حفظ الملف مؤقتاً
            file_path = f'media/temp_import_{int(time.time())}.xlsx'
            with open(file_path, 'wb+') as destination:
                for chunk in excel_file.chunks():
                    destination.write(chunk)

            # معاينة البيانات
            try:
                preview_data = []
                df = pd.read_excel(file_path)

                for index, row in df.iterrows():
                    preview_data.append({
                        'name': row.get('name', ''),
                        'sku': row.get('sku', ''),
                        'category': row.get('category', ''),
                        'unit': row.get('unit', ''),
                        'purchase_price': row.get('purchase_price', 0),
                        'selling_price': row.get('selling_price', 0),
                    })

                context = {
                    'form': form,
                    'preview_data': preview_data,
                    'file_path': file_path,
                }
                return render(request, 'products/products/bulk_import.html', context)

            except Exception as e:
                messages.error(request, f'خطأ في قراءة الملف: {str(e)}')
    else:
        form = BulkImportForm()

    return render(request, 'products/products/bulk_import.html', {'form': form})


@login_required

def bulk_import_confirm(request):
    """
    تأكيد الاستيراد الجماعي
    """
    if request.method == 'POST':
        file_path = request.POST.get('file_path')

        if file_path and os.path.exists(file_path):
            import_results = import_products_from_excel(file_path)

            # حذف الملف المؤقت
            os.remove(file_path)

            context = {
                'import_results': import_results,
            }
            return render(request, 'products/products/bulk_import.html', context)

    messages.error(request, 'لم يتم توفير ملف للاستيراد')
    return redirect('products:bulk_import')


@login_required

def download_import_template(request):
    """
    تحميل قالب الاستيراد
    """
    # إنشاء قالب Excel
    data = [
        ['name', 'sku', 'category', 'unit', 'description', 'purchase_price', 'selling_price', 'min_stock', 'max_stock',
         'is_active'],
        ['منتج مثال 1', 'SKU001', 'الإلكترونيات', 'قطعة', 'وصف المنتج مثال 1', 100, 150, 10, 100, True],
        ['منتج مثال 2', 'SKU002', 'الملابس', 'قطعة', 'وصف المنتج مثال 2', 50, 75, 5, 50, True],
    ]

    df = pd.DataFrame(data[1:], columns=data[0])

    # حفظ الملف مؤقتاً
    file_path = 'media/import_template.xlsx'
    df.to_excel(file_path, index=False, engine='openpyxl')

    # إرجاع الملف للتحميل
    with open(file_path, 'rb') as f:
        response = HttpResponse(f.read(), content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename="product_import_template.xlsx"'

    # حذف الملف المؤقت
    os.remove(file_path)

    return response


@login_required

def export_products(request):
    """
    تصدير المنتجات إلى Excel
    """
    products = Product.objects.select_related('category', 'unit').prefetch_related('inventory_items')

    # تطبيق نفس فلاتر البحث إذا وجدت
    search_query = request.GET.get('q', '')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(sku__icontains=search_query) |
            Q(barcode__icontains=search_query)
        )

    category_filter = request.GET.get('category', '')
    if category_filter:
        products = products.filter(category_id=category_filter)

    # إنشاء ملف Excel
    file_path = f'media/products_export_{int(time.time())}.xlsx'
    export_products_to_excel(products, file_path)

    # إرجاع الملف للتحميل
    with open(file_path, 'rb') as f:
        response = HttpResponse(f.read(), content_type='application/vnd.ms-excel')
        response[
            'Content-Disposition'] = f'attachment; filename="products_export_{datetime.now().strftime("%Y%m%d_%H%M")}.xlsx"'

    # حذف الملف المؤقت
    os.remove(file_path)

    return response


@login_required

def category_list(request):
    """
    عرض قائمة التصنيفات بشكل شجري
    """
    categories = Category.objects.filter(parent__isnull=True).prefetch_related('products')

    # إحصائيات
    total_categories = Category.objects.count()
    active_categories = Category.objects.filter(is_active=True).count()
    main_categories = categories.count()
    total_products = Product.objects.count()

    # توزيع أنواع التصنيفات
    category_types = []
    for choice in Category.CATEGORY_TYPES:
        count = Category.objects.filter(category_type=choice[0]).count()
        category_types.append({
            'name': choice[1],
            'count': count
        })

    context = {
        'categories': categories,
        'total_categories': total_categories,
        'active_categories': active_categories,
        'main_categories': main_categories,
        'total_products': total_products,
        'category_types': category_types,
    }
    return render(request, 'products/categories/list.html', context)


@login_required

def category_create(request):
    """
    إنشاء تصنيف جديد
    """
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            category = form.save()
            messages.success(request, f'تم إنشاء التصنيف "{category.name}" بنجاح')
            return redirect('products:category_list')
    else:
        form = CategoryForm()

    # إحصائيات للشريط الجانبي
    total_categories = Category.objects.count()
    category_types = []
    for choice in Category.CATEGORY_TYPES:
        count = Category.objects.filter(category_type=choice[0]).count()
        category_types.append({
            'name': choice[1],
            'count': count
        })

    context = {
        'form': form,
        'total_categories': total_categories,
        'category_types': category_types,
    }
    return render(request, 'products/categories/create.html', context)


@login_required

def category_update(request, pk):
    """
    تحديث تصنيف موجود
    """
    category = get_object_or_404(Category, pk=pk)

    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            category = form.save()
            messages.success(request, f'تم تحديث التصنيف "{category.name}" بنجاح')
            return redirect('products:category_detail', pk=category.pk)
    else:
        form = CategoryForm(instance=category)

    context = {
        'form': form,
        'category': category,
    }
    return render(request, 'products/categories/update.html', context)


@login_required

def category_detail(request, pk):
    """
    عرض تفاصيل التصنيف
    """
    category = get_object_or_404(Category, pk=pk)

    # المنتجات في هذا التصنيف
    products = category.products.all().order_by('-created_at')[:12]

    # التصنيفات الفرعية
    subcategories = category.get_children().all()

    # إحصائيات المخزون
    total_stock = 0
    low_stock_count = 0

    for product in category.products.all():
        stock = product.get_total_stock()
        total_stock += stock
        if stock <= product.min_stock:
            low_stock_count += 1

    # حركات المخزون الحديثة للمنتجات في هذا التصنيف
    recent_movements = StockMovement.objects.filter(
        product__category=category
    ).select_related('product').order_by('-created_at')[:10]

    # الترقيم للمنتجات
    paginator = Paginator(category.products.all(), 12)
    page_number = request.GET.get('page')
    products_page = paginator.get_page(page_number)

    context = {
        'category': category,
        'products': products_page,
        'subcategories': subcategories,
        'total_stock': total_stock,
        'low_stock_count': low_stock_count,
        'recent_movements': recent_movements,
    }
    return render(request, 'products/categories/detail.html', context)


@login_required

def unit_list(request):
    """
    عرض قائمة وحدات القياس
    """
    units = Unit.objects.annotate(
        product_count=Count('product')
    ).order_by('name')

    # إحصائيات
    total_units = units.count()
    active_units = units.filter(is_active=True).count()
    used_units = units.filter(product_count__gt=0).count()
    total_products = Product.objects.count()

    # الوحدات الأكثر استخداماً
    most_used_units = units.filter(product_count__gt=0).order_by('-product_count')[:5]

    context = {
        'units': units,
        'total_units': total_units,
        'active_units': active_units,
        'used_units': used_units,
        'total_products': total_products,
        'most_used_units': most_used_units,
    }
    return render(request, 'products/units/list.html', context)


@login_required

def unit_create(request):
    """
    إنشاء وحدة قياس جديدة
    """
    if request.method == 'POST':
        form = UnitForm(request.POST)
        if form.is_valid():
            unit = form.save()
            messages.success(request, f'تم إنشاء وحدة القياس "{unit.name}" بنجاح')
            return redirect('products:unit_list')
    else:
        form = UnitForm()

    # إحصائيات للشريط الجانبي
    total_units = Unit.objects.count()
    active_units = Unit.objects.filter(is_active=True).count()
    used_units = Unit.objects.filter(product__isnull=False).distinct().count()
    existing_units = Unit.objects.all()[:10]

    context = {
        'form': form,
        'total_units': total_units,
        'active_units': active_units,
        'used_units': used_units,
        'existing_units': existing_units,
    }
    return render(request, 'products/units/create.html', context)


@login_required

def unit_update(request, pk):
    """
    تحديث وحدة قياس موجودة
    """
    unit = get_object_or_404(Unit, pk=pk)

    if request.method == 'POST':
        form = UnitForm(request.POST, instance=unit)
        if form.is_valid():
            unit = form.save()
            messages.success(request, f'تم تحديث وحدة القياس "{unit.name}" بنجاح')
            return redirect('products:unit_list')
    else:
        form = UnitForm(instance=unit)

    # المنتجات المستخدمة لهذه الوحدة
    used_products = unit.product_set.all()[:5]
    used_products_count = unit.product_set.count()

    context = {
        'form': form,
        'unit': unit,
        'used_products': used_products,
        'used_products_count': used_products_count,
    }
    return render(request, 'products/units/update.html', context)


@login_required

def unit_delete(request, pk):
    """
    حذف وحدة قياس
    """
    unit = get_object_or_404(Unit, pk=pk)

    # التحقق من عدم استخدام الوحدة في أي منتج
    if unit.product_set.exists():
        messages.error(request, f'لا يمكن حذف وحدة القياس "{unit.name}" لأنها مستخدمة في بعض المنتجات')
        return redirect('products:unit_list')

    unit_name = unit.name
    unit.delete()
    messages.success(request, f'تم حذف وحدة القياس "{unit_name}" بنجاح')

    return redirect('products:unit_list')


@login_required

def warehouse_list(request):
    """
    عرض قائمة المخازن
    """
    warehouses = Warehouse.objects.annotate(
        products_count=Count('inventory_items'),
        total_quantity=Sum('inventory_items__quantity')
    ).order_by('warehouse_type', 'name')

    # إحصائيات
    total_warehouses = warehouses.count()
    active_warehouses = warehouses.filter(is_active=True).count()
    total_capacity = sum(warehouse.capacity for warehouse in warehouses)
    used_capacity = sum(warehouse.get_used_capacity() for warehouse in warehouses)

    # توزيع أنواع المخازن
    warehouse_types = []
    for choice in Warehouse.WAREHOUSE_TYPES:
        count = warehouses.filter(warehouse_type=choice[0]).count()
        warehouse_types.append({
            'name': choice[1],
            'count': count
        })

    # المخازن الأكثر استخداماً
    most_used_warehouses = warehouses.filter(products_count__gt=0).order_by('-total_quantity')[:5]

    context = {
        'warehouses': warehouses,
        'total_warehouses': total_warehouses,
        'active_warehouses': active_warehouses,
        'total_capacity': total_capacity,
        'used_capacity': used_capacity,
        'warehouse_types': warehouse_types,
        'most_used_warehouses': most_used_warehouses,
    }
    return render(request, 'products/warehouses/list.html', context)


@login_required

def warehouse_create(request):
    """
    إنشاء مخزن جديد
    """
    if request.method == 'POST':
        form = WarehouseForm(request.POST)
        if form.is_valid():
            warehouse = form.save()
            messages.success(request, f'تم إنشاء المخزن "{warehouse.name}" بنجاح')
            return redirect('products:warehouse_list')
    else:
        form = WarehouseForm()

    # إحصائيات للشريط الجانبي
    total_warehouses = Warehouse.objects.count()
    main_warehouses = Warehouse.objects.filter(warehouse_type='main').count()
    branch_warehouses = Warehouse.objects.filter(warehouse_type='branch').count()
    future_warehouses = Warehouse.objects.filter(warehouse_type='future').count()
    existing_warehouses = Warehouse.objects.all()[:10]

    context = {
        'form': form,
        'total_warehouses': total_warehouses,
        'main_warehouses': main_warehouses,
        'branch_warehouses': branch_warehouses,
        'future_warehouses': future_warehouses,
        'existing_warehouses': existing_warehouses,
    }
    return render(request, 'products/warehouses/create.html', context)


@login_required

def warehouse_update(request, pk):
    """
    تحديث مخزن موجود
    """
    warehouse = get_object_or_404(Warehouse, pk=pk)

    if request.method == 'POST':
        form = WarehouseForm(request.POST, instance=warehouse)
        if form.is_valid():
            warehouse = form.save()
            messages.success(request, f'تم تحديث المخزن "{warehouse.name}" بنجاح')
            return redirect('products:warehouse_detail', pk=warehouse.pk)
    else:
        form = WarehouseForm(instance=warehouse)

    # إحصائيات المخزن
    products_count = warehouse.inventory_items.count()
    total_quantity = warehouse.inventory_items.aggregate(total=Sum('quantity'))['total'] or 0
    low_stock_count = sum(1 for item in warehouse.inventory_items.all() if item.quantity <= item.product.min_stock)
    out_of_stock_count = sum(1 for item in warehouse.inventory_items.all() if item.quantity == 0)

    context = {
        'form': form,
        'warehouse': warehouse,
        'products_count': products_count,
        'total_quantity': total_quantity,
        'low_stock_count': low_stock_count,
        'out_of_stock_count': out_of_stock_count,
    }
    return render(request, 'products/warehouses/update.html', context)


@login_required

def warehouse_detail(request, pk):
    """
    عرض تفاصيل المخزن
    """
    warehouse = get_object_or_404(Warehouse, pk=pk)

    # المنتجات في المخزن
    inventory_items = warehouse.inventory_items.select_related('product', 'product__category',
                                                               'product__unit').order_by('product__name')

    # إحصائيات
    products_count = inventory_items.count()
    total_quantity = sum(item.quantity for item in inventory_items)
    total_value = sum(item.quantity * item.product.purchase_price for item in inventory_items)
    low_stock_count = sum(1 for item in inventory_items if item.quantity <= item.product.min_stock)

    # المنتجات منخفضة المخزون
    low_stock_items = [item for item in inventory_items if item.quantity <= item.product.min_stock][:5]

    # حركات المخزون الحديثة
    recent_movements = StockMovement.objects.filter(
        warehouse=warehouse
    ).select_related('product', 'created_by').order_by('-created_at')[:10]

    # الترقيم للمنتجات
    paginator = Paginator(inventory_items, 20)
    page_number = request.GET.get('page')
    inventory_items_page = paginator.get_page(page_number)

    context = {
        'warehouse': warehouse,
        'inventory_items': inventory_items_page,
        'products_count': products_count,
        'total_quantity': total_quantity,
        'total_value': total_value,
        'low_stock_count': low_stock_count,
        'low_stock_items': low_stock_items,
        'recent_movements': recent_movements,
    }
    return render(request, 'products/warehouses/detail.html', context)


@login_required

def barcode_generator(request):
    """
    مولد الباركود
    """
    products = Product.objects.all()[:50]  # عرض أول 50 منتج للاختيار
    product_id = request.GET.get('product')

    if product_id:
        product = get_object_or_404(Product, id=product_id)
    else:
        product = None

    context = {
        'products': products,
        'product': product,
    }
    return render(request, 'products/barcode/generator.html', context)


@login_required

def barcode_scanner(request):
    """
    ماسح الباركود
    """
    return render(request, 'products/barcode/scanner.html')


@login_required

def barcode_print(request):
    """
    صفحة طباعة الباركود
    """
    products = Product.objects.all()[:100]  # عرض أول 100 منتج للاختيار

    context = {
        'products': products,
    }
    return render(request, 'products/barcode/print.html', context)


@login_required

def search_by_barcode(request):
    """
    البحث عن المنتج بالباركود (للماسح)
    """
    barcode = request.GET.get('barcode', '')
    if barcode:
        try:
            product = Product.objects.get(barcode=barcode)
            return JsonResponse({
                'success': True,
                'product': {
                    'id': product.id,
                    'name': product.name,
                    'sku': product.sku,
                    'barcode': product.barcode,
                    'selling_price': str(product.selling_price),
                    'main_image': product.main_image.url if product.main_image else '',
                }
            })
        except Product.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'المنتج غير موجود'
            })

    return JsonResponse({
        'success': False,
        'message': 'لم يتم إدخال باركود'
    })





@login_required

def stock_movements(request):
    """
    عرض حركات المخزون
    """
    movements = StockMovement.objects.select_related('product', 'warehouse', 'created_by').order_by('-created_at')

    # الفلترة
    movement_type = request.GET.get('type', '')
    if movement_type:
        movements = movements.filter(movement_type=movement_type)

    product_filter = request.GET.get('product', '')
    if product_filter:
        movements = movements.filter(product_id=product_filter)

    warehouse_filter = request.GET.get('warehouse', '')
    if warehouse_filter:
        movements = movements.filter(warehouse_id=warehouse_filter)

    # إحصائيات الحركات
    total_incoming = movements.filter(
        Q(movement_type='purchase') | Q(movement_type='transfer_in')
    ).count()

    total_outgoing = movements.filter(
        Q(movement_type='sale') | Q(movement_type='transfer_out')
    ).count()

    total_adjustments = movements.filter(movement_type='adjustment').count()

    # الترقيم
    paginator = Paginator(movements, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    products = Product.objects.all()
    warehouses = Warehouse.objects.all()

    context = {
        'page_obj': page_obj,
        'products': products,
        'warehouses': warehouses,
        'total_incoming': total_incoming,
        'total_outgoing': total_outgoing,
        'total_adjustments': total_adjustments,
        'filters': {
            'type': movement_type,
            'product': product_filter,
            'warehouse': warehouse_filter,
        }
    }
    return render(request, 'products/inventory/movements.html', context)


@login_required

def stock_adjustment(request):
    """
    تسوية المخزون
    """
    if request.method == 'POST':
        form = InventoryAdjustmentForm(request.POST)
        if form.is_valid():
            adjustment = form.save(commit=False)
            adjustment.movement_type = 'adjustment'
            adjustment.created_by = request.user

            # الحصول على المخزون الحالي
            inventory_item, created = InventoryItem.objects.get_or_create(
                product=adjustment.product,
                warehouse=adjustment.warehouse,
                defaults={'quantity': 0}
            )

            adjustment.quantity_before = inventory_item.quantity
            adjustment.quantity_after = adjustment.quantity
            inventory_item.quantity = adjustment.quantity
            inventory_item.save()

            adjustment.save()
            messages.success(request, 'تم تسوية المخزون بنجاح')
            return redirect('products:stock_movements')
    else:
        form = InventoryAdjustmentForm()
        # تعيين القيم الافتراضية من query parameters
        product_id = request.GET.get('product')
        warehouse_id = request.GET.get('warehouse')

        if product_id:
            try:
                form.fields['product'].initial = product_id
            except:
                pass

        if warehouse_id:
            try:
                form.fields['warehouse'].initial = warehouse_id
            except:
                pass

    return render(request, 'products/inventory/adjustment.html', {'form': form})


@login_required

def stock_transfer(request):
    """
    تحويل المخزون بين المخازن
    """
    if request.method == 'POST':
        form = StockTransferForm(request.POST)
        if form.is_valid():
            transfer = form.save(commit=False)
            transfer.created_by = request.user

            # التحقق من توفر المخزون في المخزن المصدر
            from_inventory = InventoryItem.objects.filter(
                product=transfer.product,
                warehouse=transfer.from_warehouse
            ).first()

            if not from_inventory or from_inventory.quantity < transfer.quantity:
                messages.error(request, 'لا يوجد مخزون كافي في المخزن المصدر')
            else:
                # خصم من المخزن المصدر
                from_inventory.quantity -= transfer.quantity
                from_inventory.save()

                # إضافة إلى المخزن الهدف
                to_inventory, created = InventoryItem.objects.get_or_create(
                    product=transfer.product,
                    warehouse=transfer.to_warehouse,
                    defaults={'quantity': 0}
                )
                to_inventory.quantity += transfer.quantity
                to_inventory.save()

                # تسجيل الحركة للمخزن المصدر
                StockMovement.objects.create(
                    product=transfer.product,
                    warehouse=transfer.from_warehouse,
                    movement_type='transfer_out',
                    quantity=-transfer.quantity,
                    quantity_before=from_inventory.quantity + transfer.quantity,
                    quantity_after=from_inventory.quantity,
                    reference_number=f"TRF-{transfer.id}",
                    notes=transfer.notes,
                    created_by=request.user
                )

                # تسجيل الحركة للمخزن الهدف
                StockMovement.objects.create(
                    product=transfer.product,
                    warehouse=transfer.to_warehouse,
                    movement_type='transfer_in',
                    quantity=transfer.quantity,
                    quantity_before=to_inventory.quantity - transfer.quantity,
                    quantity_after=to_inventory.quantity,
                    reference_number=f"TRF-{transfer.id}",
                    notes=transfer.notes,
                    created_by=request.user
                )

                transfer.save()
                messages.success(request, 'تم تحويل المخزون بنجاح')
                return redirect('products:stock_movements')
    else:
        form = StockTransferForm()
        # تعيين القيم الافتراضية من query parameters
        from_warehouse_id = request.GET.get('from_warehouse')

        if from_warehouse_id:
            try:
                form.fields['from_warehouse'].initial = from_warehouse_id
            except:
                pass

    # الحصول على آخر التحويلات
    recent_transfers = StockTransfer.objects.select_related(
        'product', 'from_warehouse', 'to_warehouse'
    ).order_by('-transfer_date')[:5]

    context = {
        'form': form,
        'recent_transfers': recent_transfers,
    }
    return render(request, 'products/inventory/transfers.html', context)


@login_required

def stock_alerts(request):
    """
    عرض تنبيهات المخزون
    """
    alerts = StockAlert.objects.select_related('product', 'warehouse').order_by('-created_at')

    # إحصائيات التنبيهات
    total_alerts = alerts.count()
    low_stock_count = alerts.filter(alert_type='low_stock', is_resolved=False).count()
    expiry_count = alerts.filter(alert_type='expiry', is_resolved=False).count()
    excess_count = alerts.filter(alert_type='excess', is_resolved=False).count()
    resolved_count = alerts.filter(is_resolved=True).count()

    # فلترة التنبيهات النشطة فقط بشكل افتراضي
    show_resolved = request.GET.get('show_resolved')
    if not show_resolved:
        alerts = alerts.filter(is_resolved=False)

    context = {
        'alerts': alerts,
        'total_alerts': total_alerts,
        'low_stock_count': low_stock_count,
        'expiry_count': expiry_count,
        'excess_count': excess_count,
        'resolved_count': resolved_count,
    }
    return render(request, 'products/inventory/stock_alerts.html', context)


@login_required

def resolve_alert(request, pk):
    """
    حل تنبيه المخزون
    """
    if request.method == 'POST':
        alert = get_object_or_404(StockAlert, pk=pk)
        alert.is_resolved = True
        alert.resolved_at = datetime.now()
        alert.save()

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True})

        messages.success(request, 'تم حل التنبيه بنجاح')
        return redirect('products:stock_alerts')

    return JsonResponse({'success': False})


@login_required

def resolve_all_alerts(request):
    """
    حل جميع تنبيهات المخزون
    """
    if request.method == 'POST':
        unresolved_alerts = StockAlert.objects.filter(is_resolved=False)
        unresolved_alerts.update(
            is_resolved=True,
            resolved_at=datetime.now()
        )

        messages.success(request, f'تم حل {unresolved_alerts.count()} تنبيه بنجاح')
        return redirect('products:stock_alerts')

    return redirect('products:stock_alerts')


@login_required

def inventory_dashboard(request):
    """
    لوحة تحكم المخزون
    """
    # إحصائيات عامة
    total_products = Product.objects.count()
    total_categories = Category.objects.count()
    total_warehouses = Warehouse.objects.count()
    low_stock_alerts = StockAlert.objects.filter(is_resolved=False, alert_type='low_stock').count()

    # المنتجات منخفضة المخزون
    low_stock_products = []
    for product in Product.objects.all():
        total_stock = product.get_total_stock()
        if total_stock <= product.min_stock and product.min_stock > 0:
            low_stock_products.append({
                'product': product,
                'current_stock': total_stock,
                'min_stock': product.min_stock
            })

    # حركات المخزون الحديثة
    recent_movements = StockMovement.objects.select_related('product', 'warehouse').order_by('-created_at')[:10]

    # معلومات المخازن
    warehouses = Warehouse.objects.annotate(
        products_count=Count('inventory_items'),
        total_quantity=Sum('inventory_items__quantity')
    )[:5]

    context = {
        'total_products': total_products,
        'total_categories': total_categories,
        'total_warehouses': total_warehouses,
        'low_stock_alerts': low_stock_alerts,
        'low_stock_products': low_stock_products[:5],
        'recent_movements': recent_movements,
        'warehouses': warehouses,
    }
    return render(request, 'products/inventory/dashboard.html', context)