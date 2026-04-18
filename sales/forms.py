from django import forms
from .models import SalesInvoice, SalesItem, Customer
from products.models import Product
from inventory.models import Warehouse

class SalesInvoiceForm(forms.ModelForm):
    class Meta:
        model = SalesInvoice
        fields = ['customer', 'warehouse', 'status', 'notes']
        widgets = {
            'customer': forms.Select(attrs={'class': 'form-select'}),
            'warehouse': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class SalesItemForm(forms.ModelForm):
    class Meta:
        model = SalesItem
        fields = ['product', 'quantity', 'unit_price']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-select'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
        }

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'phone', 'email', 'address', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
