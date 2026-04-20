from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('sales/', views.sales_report, name='sales_report'),
    path('purchases/', views.purchase_report, name='purchase_report'),
]
