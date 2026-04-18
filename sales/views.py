from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.forms import inlineformset_factory
from django.db import transaction
from django.http import HttpResponse
from .models import SalesInvoice, SalesItem, Customer
from .forms import SalesInvoiceForm, SalesItemForm, CustomerForm
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from io import BytesIO

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
    return render(request, 'sales/customers/list.html', {'customers': customers})

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
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Header
    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, height - 50, f"Sales Invoice: INV-{invoice.id}")
    p.setFont("Helvetica", 12)
    p.drawString(100, height - 70, f"Customer: {invoice.customer.name if invoice.customer else 'Cash Customer'}")
    p.drawString(100, height - 85, f"Date: {invoice.created_at.strftime('%Y-%m-%d')}")
    p.drawString(100, height - 100, f"Status: {invoice.get_status_display()}")

    # Table Header
    p.line(100, height - 120, 500, height - 120)
    p.drawString(100, height - 135, "Product")
    p.drawString(300, height - 135, "Qty")
    p.drawString(350, height - 135, "Price")
    p.drawString(420, height - 135, "Total")
    p.line(100, height - 140, 500, height - 140)

    # Table Body
    y = height - 155
    for item in invoice.items.all():
        if y < 50:
            p.showPage()
            y = height - 50
        p.drawString(100, y, f"{item.product.name[:30]}")
        p.drawString(300, y, f"{item.quantity}")
        p.drawString(350, y, f"{item.unit_price}")
        p.drawString(420, y, f"{item.total_price}")
        y -= 20

    # Footer
    p.line(100, y - 10, 500, y - 10)
    p.setFont("Helvetica-Bold", 12)
    p.drawString(350, y - 25, "Grand Total:")
    p.drawString(420, y - 25, f"{invoice.total_amount}")

    p.showPage()
    p.save()
    
    buffer.seek(0)
    return HttpResponse(buffer, content_type='application/pdf', 
                        headers={'Content-Disposition': f'attachment; filename="Invoice_{invoice.id}.pdf"'})
