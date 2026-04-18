from django import forms
from .models import *
from inventory.models import Warehouse, InventoryItem, StockMovement, StockTransfer, StockAlert
from .models import Unit

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'parent', 'description', 'image', 'category_type', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'أدخل اسم التصنيف'}),
            'parent': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'category_type': forms.Select(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'name', 'sku', 'category', 'unit', 'description',
            'purchase_price', 'selling_price', 'min_stock', 'max_stock',
            'main_image', 'has_expiry', 'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'sku': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'unit': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'purchase_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'selling_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'min_stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'max_stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'has_expiry': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ['image', 'caption', 'is_default']


class WarehouseForm(forms.ModelForm):
    class Meta:
        model = Warehouse
        fields = ['name', 'code', 'warehouse_type', 'address', 'manager', 'capacity', 'phone', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'warehouse_type': forms.Select(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'manager': forms.Select(attrs={'class': 'form-control'}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class InventoryAdjustmentForm(forms.ModelForm):
    class Meta:
        model = StockMovement
        fields = ['product', 'warehouse', 'quantity', 'notes']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-control'}),
            'warehouse': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class StockTransferForm(forms.ModelForm):
    class Meta:
        model = StockTransfer
        fields = ['product', 'from_warehouse', 'to_warehouse', 'quantity', 'notes']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-control'}),
            'from_warehouse': forms.Select(attrs={'class': 'form-control'}),
            'to_warehouse': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class BulkImportForm(forms.Form):
    excel_file = forms.FileField(
        label='ملف Excel',
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.xlsx,.xls'})
    )





class UnitForm(forms.ModelForm):
    class Meta:
        model = Unit
        fields = ['name', 'symbol', 'conversion_factor', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'أدخل اسم الوحدة'
            }),
            'symbol': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'أدخل رمز الوحدة'
            }),
            'conversion_factor': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.001',
                'min': '0.001'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }

    def clean_conversion_factor(self):
        conversion_factor = self.cleaned_data.get('conversion_factor')
        if conversion_factor <= 0:
            raise forms.ValidationError('عامل التحويل يجب أن يكون رقم موجب')
        return conversion_factor

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if Unit.objects.filter(name=name).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('هذه الوحدة موجودة مسبقاً')
        return name

    def clean_symbol(self):
        symbol = self.cleaned_data.get('symbol')
        if Unit.objects.filter(symbol=symbol).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('هذا الرمز مستخدم مسبقاً')
        return symbol
