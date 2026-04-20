from django.urls import path
from . import views
from .views import (CustomPasswordChangeView, CustomPasswordResetView,
                    CustomPasswordResetConfirmView, UserDeleteView, UserDetailView,
                    RoleCreateView, RoleUpdateView, ActivityDetailView)

app_name = 'accounts'

urlpatterns = [
    # --- روابط المصادقة (Authentication) ---
    path('', views.custom_login, name='login'),  # صفحة تسجيل الدخول (الصفحة الرئيسية للتطبيق)
    path('logout/', views.custom_logout, name='logout'),  # رابط تسجيل الخروج
    path('register/', views.UserCreateView.as_view(), name='register'),  # تسجيل مستخدم جديد
    path('password/change/', CustomPasswordChangeView.as_view(), name='password_change'),  # تغيير كلمة المرور
    path('password/reset/', CustomPasswordResetView.as_view(), name='password_reset'),  # طلب استعادة كلمة المرور
    path('password/reset/confirm/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(),
         name='password_reset_confirm'),  # تأكيد تعيين كلمة المرور الجديدة عبر البريد

    # --- لوحات التحكم (Dashboards) ---
    path('dashboard/', views.dashboard, name='dashboard'),  # لوحة التحكم العامة لعمليات المستودع
    path('users/dashboard/', views.user_dashboard, name='user_dashboard'),  # لوحة تحكم خاصة بإدارة المستخدمين والأنشطة

    # --- إدارة المستخدمين (Users Management) ---
    path('users/', views.UserListView.as_view(), name='user_list'),  # قائمة كافة المستخدمين
    path('users/create/', views.UserCreateView.as_view(), name='user_create'),  # إضافة مستخدم جديد من قبل المسؤول
    path('users/<int:pk>/', UserDetailView.as_view(), name='user_detail'),  # عرض تفاصيل مستخدم معين
    path('users/<int:pk>/update/', views.UserUpdateView.as_view(), name='user_update'),  # تعديل بيانات مستخدم
    path('users/<int:pk>/delete/', UserDeleteView.as_view(), name='user_delete'),  # حذف مستخدم من النظام
    path('profile/', views.user_profile, name='profile'),  # صفحة الملف الشخصي للمستخدم الحالي

    # --- إدارة الأدوار والصلاحيات (Roles & Permissions) ---
    path('roles/', views.RoleListView.as_view(), name='role_list'),  # عرض قائمة المسميات الوظيفية (الأدوار)
    path('roles/create/', RoleCreateView.as_view(), name='role_create'),  # إضافة مسمى وظيفي جديد
    path('roles/<int:pk>/update/', RoleUpdateView.as_view(), name='role_update'),  # تعديل بيانات المسمى الوظيفي
    path('roles/<int:pk>/permissions/', views.role_permissions, name='role_permissions'),  # التحكم الدقيق في صلاحيات الدور

    # --- سجلات الأنشطة (Activity Logs) ---
    path('activity/', views.ActivityLogListView.as_view(), name='activity_logs'),  # سجل تتبع العمليات في النظام
    path('activity/<int:pk>/', ActivityDetailView.as_view(), name='activity_detail'),  # تفاصيل عملية محددة من السجل
]
