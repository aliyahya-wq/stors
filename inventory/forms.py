from django import forms
from .models import *


class WarehouseForm(forms.ModelForm):
    class Meta:
        model = Warehouse
        fields = ['name', 'code', 'address', 'capacity', 'status', 'manager']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'manager': forms.Select(attrs={'class': 'form-control'}),
        }


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'sku', 'barcode', 'category', 'description',
                  'cost_price', 'selling_price', 'min_stock', 'max_stock', 'unit', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'sku': forms.TextInput(attrs={'class': 'form-control'}),
            'barcode': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'cost_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'selling_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'min_stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'max_stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'unit': forms.TextInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class StockMovementForm(forms.ModelForm):
    class Meta:
        model = StockMovement
        fields = ['movement_type', 'product', 'from_warehouse', 'to_warehouse', 'quantity', 'notes']
        widgets = {
            'movement_type': forms.Select(attrs={'class': 'form-control', 'id': 'movement_type'}),
            'product': forms.Select(attrs={'class': 'form-control'}),
            'from_warehouse': forms.Select(attrs={'class': 'form-control', 'id': 'from_warehouse'}),
            'to_warehouse': forms.Select(attrs={'class': 'form-control', 'id': 'to_warehouse'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class InventoryCountForm(forms.ModelForm):
    class Meta:
        model = InventoryCount
        fields = ['warehouse']
        widgets = {
            'warehouse': forms.Select(attrs={'class': 'form-control'}),
        }


class CountItemForm(forms.ModelForm):
    class Meta:
        model = CountItem
        fields = ['actual_quantity']
        widgets = {
            'actual_quantity': forms.NumberInput(attrs={'class': 'form-control'}),
        }
