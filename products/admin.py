from django.contrib import admin
from .models import *


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'category_type', 'is_active', 'get_products_count']
    list_filter = ['category_type', 'is_active']
    search_fields = ['name']
    prepopulated_fields = {'slug': ['name']}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'sku', 'barcode', 'category', 'selling_price', 'is_active']
    list_filter = ['category', 'is_active']
    search_fields = ['name', 'sku', 'barcode']
    readonly_fields = ['created_at', 'updated_at']


