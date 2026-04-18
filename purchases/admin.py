from django.contrib import admin
from .models import Supplier, PurchaseOrder, PurchaseItem

class PurchaseItemInline(admin.TabularInline):
    model = PurchaseItem
    extra = 1

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'email', 'is_active', 'created_at')
    search_fields = ('name', 'phone')

@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'supplier', 'warehouse', 'status', 'total_amount', 'created_at')
    list_filter = ('status', 'warehouse')
    search_fields = ('supplier__name', 'id')
    inlines = [PurchaseItemInline]
