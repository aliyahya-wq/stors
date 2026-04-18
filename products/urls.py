from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    # لوحة التحكم الرئيسية
    path('', views.dashboard, name='product_dashboard'),
    path('inventory/', views.inventory_dashboard, name='inventory_dashboard'),

    # ==================== التصنيفات ====================
    path('categories/', views.category_list, name='category_list'),
    path('categories/create/', views.category_create, name='category_create'),
    path('categories/<int:pk>/', views.category_detail, name='category_detail'),
    path('categories/<int:pk>/update/', views.category_update, name='category_update'),

    # ==================== المنتجات ====================
    path('products/', views.product_list, name='product_list'),
    path('products/create/', views.product_create, name='product_create'),
    path('products/<int:pk>/', views.product_detail, name='product_detail'),
    path('products/<int:pk>/update/', views.product_update, name='product_update'),
    path('products/search/', views.product_search, name='product_search'),

    # ==================== الاستيراد والتصدير ====================
    path('products/import/', views.bulk_import, name='bulk_import'),
    path('products/import/confirm/', views.bulk_import_confirm, name='bulk_import_confirm'),
    path('products/import/template/', views.download_import_template, name='download_import_template'),
    path('products/export/', views.export_products, name='export_products'),

    # ==================== وحدات القياس ====================
    path('units/', views.unit_list, name='unit_list'),
    path('units/create/', views.unit_create, name='unit_create'),
    path('units/<int:pk>/update/', views.unit_update, name='unit_update'),
    path('units/<int:pk>/delete/', views.unit_delete, name='unit_delete'),

    # ==================== المخازن ====================
    path('warehouses/', views.warehouse_list, name='warehouse_list'),
    path('warehouses/create/', views.warehouse_create, name='warehouse_create'),
    path('warehouses/<int:pk>/', views.warehouse_detail, name='warehouse_detail'),
    path('warehouses/<int:pk>/update/', views.warehouse_update, name='warehouse_update'),

    # ==================== إدارة المخزون ====================
    path('inventory/movements/', views.stock_movements, name='stock_movements'),
    path('inventory/adjustment/', views.stock_adjustment, name='stock_adjustment'),
    path('inventory/transfer/', views.stock_transfer, name='stock_transfer'),
    path('inventory/transfers/', views.stock_transfer, name='stock_transfers'),  # alias
    path('inventory/alerts/', views.stock_alerts, name='stock_alerts'),
    path('inventory/alerts/<int:pk>/resolve/', views.resolve_alert, name='resolve_alert'),
    path('inventory/alerts/resolve-all/', views.resolve_all_alerts, name='resolve_all_alerts'),

    # ==================== الباركود ====================
    path('barcode/generator/', views.barcode_generator, name='barcode_generator'),
    path('barcode/scanner/', views.barcode_scanner, name='barcode_scanner'),
    path('barcode/print/', views.barcode_print, name='barcode_print'),
    path('barcode/search/', views.search_by_barcode, name='search_by_barcode'),
]