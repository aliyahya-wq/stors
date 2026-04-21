from django import forms
from .models import *
from inventory.models import Warehouse, InventoryItem, StockMovement, StockTransfer, StockAlert
from .models import Unit

# نموذج التصنيفات: يستخدم لإنشاء وتعديل فئات المنتجات في النظام 
class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'parent', 'description', 'image', 'category_type', 'is_active']
        # استخدام التنسيقات (Widgets) لضمان توافق الحقول مع تصميم واجهة المستخدم (Bootstrap)
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'أدخل اسم التصنيف'}),
            'parent': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'category_type': forms.Select(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


# نموذج المنتجات: النموذج الأساسي لإضافة بيانات الأصناف المخزنة وتعديلها 
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'name', 'sku', 'category', 'unit', 'description',
            'purchase_price', 'selling_price', 'min_stock', 'max_stock',
            'main_image', 'has_expiry', 'is_active'
        ]
        # الربط بين حقول قاعدة البيانات وعناصر واجهة الإدخال مع إضافة فئات CSS المناسبة
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


# نموذج معرض الصور: لإضافة صور إضافية لكل منتج لتوفير رؤية أشمل للصنف 
class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ['image', 'caption', 'is_default']


# نموذج المستودعات: لتعريف وتحديث بيانات مواقع التخزين المختلفة 
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


# نموذج تسوية المخزون: يستخدم في عمليات الجرد والتعديل اليدوي للكميات 
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


# نموذج تحويل المخزون: للتعامل مع نقل الأصناف بين المستودعات بمان يضمن التوثيق الدقيق 
class StockTransferForm(forms.ModelForm):
    class Meta:
        model = StockTransfer
        fields = ['product', 'from_warehouse', 'to_warehouse', 'quantity', 'notes']
        # توجيه المستخدم لاختيار المستودعات والكميات المطلوبة بشكل منظم
        widgets = {
            'product': forms.Select(attrs={'class': 'form-control'}),
            'from_warehouse': forms.Select(attrs={'class': 'form-control'}),
            'to_warehouse': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


# نموذج الاستيراد الجماعي: نموذج بسيط لالتقاط ملفات الإكسل ومعالجتها 
class BulkImportForm(forms.Form):
    excel_file = forms.FileField(
        label='ملف Excel',
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.xlsx,.xls'})
    )


# نموذج وحدات القياس: لتعريف كيفية قياس المنتجات (كجم، متر، إلخ) 
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

    # منطق التحقق (Validation Logic) لضمان جودة البيانات المدخلة في الوحدات
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
