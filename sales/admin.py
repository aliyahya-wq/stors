from django.contrib import admin
from .models import Customer, SalesInvoice, SalesItem

class SalesItemInline(admin.TabularInline):
    model = SalesItem
    extra = 1

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'email', 'is_active', 'created_at')
    search_fields = ('name', 'phone')

@admin.register(SalesInvoice)
class SalesInvoiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'warehouse', 'status', 'total_amount', 'created_at')
    list_filter = ('status', 'warehouse')
    search_fields = ('customer__name', 'id')
    inlines = [SalesItemInline]
