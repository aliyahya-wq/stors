from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.forms import inlineformset_factory
from django.db import transaction
from .models import SalesInvoice, SalesItem, Customer
from .forms import SalesInvoiceForm, SalesItemForm

@login_required
def dashboard(request):
    recent_sales = SalesInvoice.objects.select_related('customer').order_by('-created_at')[:10]
    total_sales = SalesInvoice.objects.count()
    pending_sales = SalesInvoice.objects.filter(status='pending').count()
    total_customers = Customer.objects.count()
    
    from django.db.models import Sum
    total_value = SalesInvoice.objects.aggregate(t=Sum('total_amount'))['t'] or 0

    context = {
        'recent_sales': recent_sales,
        'total_sales': total_sales,
        'pending_sales': pending_sales,
        'total_customers': total_customers,
        'total_value': total_value,
    }
    return render(request, 'sales/dashboard.html', context)

@login_required
def create_sale(request):
    SalesItemFormSet = inlineformset_factory(
        SalesInvoice, 
        SalesItem, 
        form=SalesItemForm, 
        extra=3, 
        can_delete=True
    )

    if request.method == 'POST':
        form = SalesInvoiceForm(request.POST)
        formset = SalesItemFormSet(request.POST)
        
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                sales_invoice = form.save(commit=False)
                sales_invoice.created_by = request.user
                sales_invoice.save()
                
                formset.instance = sales_invoice
                formset.save()

                # Update total amount
                total = sum(item.total_price for item in sales_invoice.items.all())
                sales_invoice.total_amount = total
                sales_invoice.save()

            messages.success(request, 'تم إصدار الفاتورة بنجاح.')
            return redirect('sales:dashboard')
    else:
        form = SalesInvoiceForm()
        formset = SalesItemFormSet()

    context = {
        'form': form,
        'formset': formset,
    }
    return render(request, 'sales/create.html', context)
