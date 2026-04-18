from django.urls import path
from . import views
from .views import (CustomPasswordChangeView, CustomPasswordResetView,
                    CustomPasswordResetConfirmView, UserDeleteView, UserDetailView,
                    RoleCreateView, RoleUpdateView, ActivityDetailView)

app_name = 'accounts'

urlpatterns = [
    # Authentication
    path('', views.custom_login, name='login'),
    path('logout/', views.custom_logout, name='logout'),
    path('register/', views.UserCreateView.as_view(), name='register'),
    path('password/change/', CustomPasswordChangeView.as_view(), name='password_change'),
    path('password/reset/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('password/reset/confirm/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(),
         name='password_reset_confirm'),

    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),

    # Users
    path('users/', views.UserListView.as_view(), name='user_list'),
    path('users/create/', views.UserCreateView.as_view(), name='user_create'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='user_detail'),
    path('users/<int:pk>/update/', views.UserUpdateView.as_view(), name='user_update'),
    path('users/<int:pk>/delete/', UserDeleteView.as_view(), name='user_delete'),
    path('profile/', views.user_profile, name='profile'),

    # Roles
    path('roles/', views.RoleListView.as_view(), name='role_list'),
    path('roles/create/', RoleCreateView.as_view(), name='role_create'),
    path('roles/<int:pk>/update/', RoleUpdateView.as_view(), name='role_update'),
    path('roles/<int:pk>/permissions/', views.role_permissions, name='role_permissions'),

    # Activity Logs
    path('activity/', views.ActivityLogListView.as_view(), name='activity_logs'),
    path('activity/<int:pk>/', ActivityDetailView.as_view(), name='activity_detail'),
]
