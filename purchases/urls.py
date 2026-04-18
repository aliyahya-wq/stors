from django.urls import path
from . import views

app_name = 'purchases'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('create/', views.create_purchase, name='create'),
    path('reports/', views.reports, name='reports'),
]
