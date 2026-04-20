from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.forms import inlineformset_factory
from django.db import transaction
from django.db.models import Q, Sum
from django.core.paginator import Paginator
from django.http import HttpResponse
from .models import PurchaseOrder, PurchaseItem, Supplier
from .forms import PurchaseOrderForm, PurchaseItemForm, SupplierForm
from core.pdf_utils import generate_purchase_pdf

@login_required
def dashboard(request):
    recent_purchases = PurchaseOrder.objects.select_related('supplier').order_by('-created_at')[:10]
    total_purchases = PurchaseOrder.objects.count()
    pending_purchases = PurchaseOrder.objects.filter(status='pending').count()
    total_suppliers = Supplier.objects.count()
    
    from django.db.models import Sum
    total_value = PurchaseOrder.objects.aggregate(t=Sum('total_amount'))['t'] or 0

    context = {
        'recent_purchases': recent_purchases,
        'total_purchases': total_purchases,
        'pending_purchases': pending_purchases,
        'total_suppliers': total_suppliers,
        'total_value': total_value,
    }
    return render(request, 'purchases/dashboard.html', context)

# Suppliers Views
@login_required
def supplier_list(request):
    suppliers = Supplier.objects.all()

    # بحث
    q = request.GET.get('q', '').strip()
    if q:
        suppliers = suppliers.filter(
            Q(name__icontains=q) |
            Q(phone__icontains=q) |
            Q(email__icontains=q) |
            Q(address__icontains=q)
        )

    # فلترة بالحالة
    status = request.GET.get('status', '')
    if status == 'active':
        suppliers = suppliers.filter(is_active=True)
    elif status == 'inactive':
        suppliers = suppliers.filter(is_active=False)

    # ترتيب
    sort = request.GET.get('sort', '-created_at')
    if sort in ['name', '-name', 'created_at', '-created_at']:
        suppliers = suppliers.order_by(sort)

    # ترقيم الصفحات
    paginator = Paginator(suppliers, 10)
    page = request.GET.get('page')
    suppliers = paginator.get_page(page)

    context = {
        'suppliers': suppliers,
        'q': q,
        'status': status,
        'sort': sort,
        'total_active': Supplier.objects.filter(is_active=True).count(),
        'total_inactive': Supplier.objects.filter(is_active=False).count(),
        'total_count': Supplier.objects.count(),
    }
    return render(request, 'purchases/suppliers/list.html', context)

@login_required
def supplier_create(request):
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم إضافة المورد بنجاح.')
            return redirect('purchases:supplier_list')
    else:
        form = SupplierForm()
    return render(request, 'purchases/suppliers/form.html', {'form': form, 'title': 'إضافة مورد جديد'})

@login_required
def supplier_detail(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    orders = supplier.purchaseorder_set.all()
    return render(request, 'purchases/suppliers/detail.html', {'supplier': supplier, 'orders': orders})

@login_required
def supplier_update(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == 'POST':
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تحديث بيانات المورد بنجاح.')
            return redirect('purchases:supplier_list')
    else:
        form = SupplierForm(instance=supplier)
    return render(request, 'purchases/suppliers/form.html', {'form': form, 'title': 'تعديل بيانات مورد'})

@login_required
def supplier_delete(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == 'POST':
        supplier.delete()
        messages.success(request, 'تم حذف المورد بنجاح.')
        return redirect('purchases:supplier_list')
    return render(request, 'purchases/suppliers/confirm_delete.html', {'supplier': supplier})

# Purchase Orders Views
@login_required
def purchase_list(request):
    orders = PurchaseOrder.objects.select_related('supplier', 'warehouse').all()
    return render(request, 'purchases/orders/list.html', {'orders': orders})

@login_required
def create_purchase(request):
    PurchaseItemFormSet = inlineformset_factory(
        PurchaseOrder, 
        PurchaseItem, 
        form=PurchaseItemForm, 
        extra=3, 
        can_delete=True
    )

    if request.method == 'POST':
        form = PurchaseOrderForm(request.POST)
        formset = PurchaseItemFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                purchase_order = form.save(commit=False)
                purchase_order.created_by = request.user
                purchase_order.save()
                
                formset.instance = purchase_order
                formset.save()

                # Update total amount
                total = sum(item.total_price for item in purchase_order.items.all())
                purchase_order.total_amount = total
                purchase_order.save()

            messages.success(request, 'تم إضافة طلب الشراء بنجاح.')
            return redirect('purchases:purchase_list')
    else:
        form = PurchaseOrderForm()
        formset = PurchaseItemFormSet()

    context = {
        'form': form,
        'formset': formset,
    }
    return render(request, 'purchases/orders/form.html', context)

@login_required
def purchase_detail(request, pk):
    order = get_object_or_404(PurchaseOrder.objects.select_related('supplier', 'warehouse', 'created_by'), pk=pk)
    items = order.items.select_related('product')
    return render(request, 'purchases/orders/detail.html', {'order': order, 'items': items})

@login_required
def purchase_update(request, pk):
    order = get_object_or_404(PurchaseOrder, pk=pk)
    PurchaseItemFormSet = inlineformset_factory(
        PurchaseOrder, 
        PurchaseItem, 
        form=PurchaseItemForm, 
        extra=1, 
        can_delete=True
    )

    if request.method == 'POST':
        form = PurchaseOrderForm(request.POST, instance=order)
        formset = PurchaseItemFormSet(request.POST, instance=order)
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                form.save()
                formset.save()
                
                # Recalculate total amount
                total = sum(item.total_price for item in order.items.all())
                order.total_amount = total
                order.save()

            messages.success(request, 'تم تحديث طلب الشراء بنجاح.')
            return redirect('purchases:purchase_detail', pk=pk)
    else:
        form = PurchaseOrderForm(instance=order)
        formset = PurchaseItemFormSet(instance=order)

    return render(request, 'purchases/orders/form.html', {'form': form, 'formset': formset, 'is_update': True})

@login_required
def purchase_delete(request, pk):
    order = get_object_or_404(PurchaseOrder, pk=pk)
    if request.method == 'POST':
        order.delete()
        messages.success(request, 'تم حذف طلب الشراء بنجاح.')
        return redirect('purchases:purchase_list')
    return render(request, 'purchases/orders/confirm_delete.html', {'order': order})

@login_required
def purchase_pdf(request, pk):
    order = get_object_or_404(PurchaseOrder, pk=pk)
    buffer = generate_purchase_pdf(order)
    filename = f"PurchaseOrder_PO-{order.id:04d}.pdf"
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{filename}"'
    return response

@login_required
def reports(request):
    return render(request, 'purchases/dashboard.html')
