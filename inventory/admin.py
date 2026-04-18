from django.contrib import admin
from .models import Warehouse, InventoryItem, StockMovement, StockTransfer, StockAlert

@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'warehouse_type', 'manager', 'is_active']
    list_filter = ['warehouse_type', 'is_active']
    search_fields = ['name', 'code']


@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ['product', 'warehouse', 'quantity', 'expiry_date']
    list_filter = ['warehouse']
    search_fields = ['product__name']


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ['product', 'warehouse', 'movement_type', 'quantity', 'created_at', 'created_by']
    list_filter = ['movement_type', 'warehouse', 'created_at']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'


@admin.register(StockAlert)
class StockAlertAdmin(admin.ModelAdmin):
    list_display = ['product', 'alert_type', 'is_resolved', 'created_at']
    list_filter = ['alert_type', 'is_resolved']
    readonly_fields = ['created_at']
