from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.forms import inlineformset_factory
from django.db import transaction
from .models import PurchaseOrder, PurchaseItem, Supplier
from .forms import PurchaseOrderForm, PurchaseItemForm

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
            return redirect('purchases:dashboard')
    else:
        form = PurchaseOrderForm()
        formset = PurchaseItemFormSet()

    context = {
        'form': form,
        'formset': formset,
    }
    return render(request, 'purchases/create.html', context)

@login_required
def reports(request):
    return render(request, 'purchases/dashboard.html')
