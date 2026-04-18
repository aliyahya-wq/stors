import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'warehouse_system.settings')
django.setup()

from accounts.models import UserRole, CustomUser

# Create Role
super_admin_role, _ = UserRole.objects.get_or_create(
    name='super_admin',
    defaults={'display_name': 'المدير العام', 'description': 'الصلاحيات الكاملة'}
)

# Create User
if not CustomUser.objects.filter(email='admin@example.com').exists():
    CustomUser.objects.create_superuser(
        email='admin@example.com',
        password='admin',
        role=super_admin_role,
        first_name='مدير',
        last_name='النظام'
    )
    print("Admin created successfully.")
else:
    print("Admin already exists.")
