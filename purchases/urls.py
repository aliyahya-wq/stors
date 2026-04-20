from django.urls import path
from . import views

app_name = 'purchases'

urlpatterns = [
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Suppliers
    path('suppliers/', views.supplier_list, name='supplier_list'),
    path('suppliers/create/', views.supplier_create, name='supplier_create'),
    path('suppliers/<int:pk>/', views.supplier_detail, name='supplier_detail'),
    path('suppliers/<int:pk>/update/', views.supplier_update, name='supplier_update'),
    path('suppliers/<int:pk>/delete/', views.supplier_delete, name='supplier_delete'),

    # Purchase Orders
    path('orders/', views.purchase_list, name='purchase_list'),
    path('orders/create/', views.create_purchase, name='create'),
    path('orders/<int:pk>/', views.purchase_detail, name='purchase_detail'),
    path('orders/<int:pk>/update/', views.purchase_update, name='purchase_update'),
    path('orders/<int:pk>/delete/', views.purchase_delete, name='purchase_delete'),
    path('orders/<int:pk>/pdf/', views.purchase_pdf, name='purchase_pdf'),

    path('reports/', views.reports, name='reports'),
]
