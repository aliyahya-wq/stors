from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.forms import inlineformset_factory
from django.db import transaction
from django.db.models import Q, Sum
from django.core.paginator import Paginator
from django.http import HttpResponse
from .models import SalesInvoice, SalesItem, Customer
from .forms import SalesInvoiceForm, SalesItemForm, CustomerForm
from core.pdf_utils import generate_invoice_pdf

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

# Customers Views
@login_required
def customer_list(request):
    customers = Customer.objects.all()

    # بحث
    q = request.GET.get('q', '').strip()
    if q:
        customers = customers.filter(
            Q(name__icontains=q) |
            Q(phone__icontains=q) |
            Q(email__icontains=q) |
            Q(address__icontains=q)
        )

    # فلترة بالحالة
    status = request.GET.get('status', '')
    if status == 'active':
        customers = customers.filter(is_active=True)
    elif status == 'inactive':
        customers = customers.filter(is_active=False)

    # ترتيب
    sort = request.GET.get('sort', '-created_at')
    if sort in ['name', '-name', 'created_at', '-created_at']:
        customers = customers.order_by(sort)

    # ترقيم الصفحات
    paginator = Paginator(customers, 10)
    page = request.GET.get('page')
    customers = paginator.get_page(page)

    context = {
        'customers': customers,
        'q': q,
        'status': status,
        'sort': sort,
        'total_active': Customer.objects.filter(is_active=True).count(),
        'total_inactive': Customer.objects.filter(is_active=False).count(),
        'total_count': Customer.objects.count(),
    }
    return render(request, 'sales/customers/list.html', context)

@login_required
def customer_create(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم إضافة العميل بنجاح.')
            return redirect('sales:customer_list')
    else:
        form = CustomerForm()
    return render(request, 'sales/customers/form.html', {'form': form, 'title': 'إضافة عميل جديد'})

@login_required
def customer_detail(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    invoices = customer.salesinvoice_set.all()
    return render(request, 'sales/customers/detail.html', {'customer': customer, 'invoices': invoices})

@login_required
def customer_update(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تحديث بيانات العميل بنجاح.')
            return redirect('sales:customer_list')
    else:
        form = CustomerForm(instance=customer)
    return render(request, 'sales/customers/form.html', {'form': form, 'title': 'تعديل بيانات عميل'})

@login_required
def customer_delete(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        customer.delete()
        messages.success(request, 'تم حذف العميل بنجاح.')
        return redirect('sales:customer_list')
    return render(request, 'sales/customers/confirm_delete.html', {'customer': customer})

# Sales Invoices Views
@login_required
def invoice_list(request):
    invoices = SalesInvoice.objects.select_related('customer', 'warehouse').all()
    return render(request, 'sales/invoices/list.html', {'invoices': invoices})

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

            messages.success(request, 'تم إضافة الفاتورة بنجاح.')
            return redirect('sales:invoice_list')
    else:
        form = SalesInvoiceForm()
        formset = SalesItemFormSet()

    context = {
        'form': form,
        'formset': formset,
    }
    return render(request, 'sales/invoices/form.html', context)

@login_required
def invoice_detail(request, pk):
    invoice = get_object_or_404(SalesInvoice.objects.select_related('customer', 'warehouse', 'created_by'), pk=pk)
    items = invoice.items.select_related('product')
    return render(request, 'sales/invoices/detail.html', {'invoice': invoice, 'items': items})

@login_required
def invoice_update(request, pk):
    invoice = get_object_or_404(SalesInvoice, pk=pk)
    SalesItemFormSet = inlineformset_factory(
        SalesInvoice, 
        SalesItem, 
        form=SalesItemForm, 
        extra=1, 
        can_delete=True
    )

    if request.method == 'POST':
        form = SalesInvoiceForm(request.POST, instance=invoice)
        formset = SalesItemFormSet(request.POST, instance=invoice)
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                form.save()
                formset.save()
                
                # Recalculate total amount
                total = sum(item.total_price for item in invoice.items.all())
                invoice.total_amount = total
                invoice.save()

            messages.success(request, 'تم تحديث الفاتورة بنجاح.')
            return redirect('sales:invoice_detail', pk=pk)
    else:
        form = SalesInvoiceForm(instance=invoice)
        formset = SalesItemFormSet(instance=invoice)

    return render(request, 'sales/invoices/form.html', {'form': form, 'formset': formset, 'is_update': True})

@login_required
def invoice_delete(request, pk):
    invoice = get_object_or_404(SalesInvoice, pk=pk)
    if request.method == 'POST':
        invoice.delete()
        messages.success(request, 'تم حذف الفاتورة بنجاح.')
        return redirect('sales:invoice_list')
    return render(request, 'sales/invoices/confirm_delete.html', {'invoice': invoice})

@login_required
def invoice_pdf(request, pk):
    invoice = get_object_or_404(SalesInvoice, pk=pk)
    buffer = generate_invoice_pdf(invoice)
    filename = f"Invoice_INV-{invoice.id:04d}.pdf"
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{filename}"'
    return response

