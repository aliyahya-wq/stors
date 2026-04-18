from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from accounts.models import UserRole, Permission, CustomUser
from django.utils import timezone


class Command(BaseCommand):
    help = 'إنشاء بيانات افتراضية للمستخدمين والأدوار والصلاحيات'

    def handle(self, *args, **kwargs):
        self.stdout.write('جاري إنشاء البيانات الافتراضية...')

        # إنشاء الصلاحيات أولاً
        permissions = self.create_permissions()

        # إنشاء الأدوار
        roles = self.create_roles(permissions)

        # إنشاء المستخدمين
        self.create_users(roles)

        self.stdout.write(
            self.style.SUCCESS('✅ تم إنشاء البيانات الافتراضية بنجاح!')
        )

    def create_permissions(self):
        """إنشاء الصلاحيات الأساسية"""
        permissions_data = [
            # صلاحيات إدارة المستخدمين
            {'name': 'عرض المستخدمين', 'codename': 'view_users', 'module': 'users',
             'description': 'القدرة على عرض قائمة المستخدمين'},
            {'name': 'إضافة مستخدمين', 'codename': 'add_users', 'module': 'users',
             'description': 'القدرة على إضافة مستخدمين جدد'},
            {'name': 'تعديل المستخدمين', 'codename': 'change_users', 'module': 'users',
             'description': 'القدرة على تعديل بيانات المستخدمين'},
            {'name': 'حذف المستخدمين', 'codename': 'delete_users', 'module': 'users',
             'description': 'القدرة على حذف المستخدمين'},

            # صلاحيات إدارة الأدوار
            {'name': 'عرض الأدوار', 'codename': 'view_roles', 'module': 'roles',
             'description': 'القدرة على عرض قائمة الأدوار'},
            {'name': 'إضافة أدوار', 'codename': 'add_roles', 'module': 'roles',
             'description': 'القدرة على إضافة أدوار جديدة'},
            {'name': 'تعديل الأدوار', 'codename': 'change_roles', 'module': 'roles',
             'description': 'القدرة على تعديل الأدوار'},
            {'name': 'حذف الأدوار', 'codename': 'delete_roles', 'module': 'roles',
             'description': 'القدرة على حذف الأدوار'},

            # صلاحيات المنتجات
            {'name': 'عرض المنتجات', 'codename': 'view_products', 'module': 'products',
             'description': 'القدرة على عرض المنتجات'},
            {'name': 'إضافة منتجات', 'codename': 'add_products', 'module': 'products',
             'description': 'القدرة على إضافة منتجات جديدة'},
            {'name': 'تعديل المنتجات', 'codename': 'change_products', 'module': 'products',
             'description': 'القدرة على تعديل المنتجات'},
            {'name': 'حذف المنتجات', 'codename': 'delete_products', 'module': 'products',
             'description': 'القدرة على حذف المنتجات'},

            # صلاحيات المخزون
            {'name': 'عرض المخزون', 'codename': 'view_inventory', 'module': 'inventory',
             'description': 'القدرة على عرض المخزون'},
            {'name': 'إدارة المخزون', 'codename': 'manage_inventory', 'module': 'inventory',
             'description': 'القدرة على إدارة المخزون'},
            {'name': 'تعديل المخزون', 'codename': 'change_inventory', 'module': 'inventory',
             'description': 'القدرة على تعديل كميات المخزون'},

            # صلاحيات المبيعات
            {'name': 'عرض المبيعات', 'codename': 'view_sales', 'module': 'sales',
             'description': 'القدرة على عرض المبيعات'},
            {'name': 'إضافة مبيعات', 'codename': 'add_sales', 'module': 'sales',
             'description': 'القدرة على إضافة فواتير بيع'},
            {'name': 'تعديل المبيعات', 'codename': 'change_sales', 'module': 'sales',
             'description': 'القدرة على تعديل المبيعات'},
            {'name': 'حذف المبيعات', 'codename': 'delete_sales', 'module': 'sales',
             'description': 'القدرة على حذف فواتير البيع'},

            # صلاحيات المشتريات
            {'name': 'عرض المشتريات', 'codename': 'view_purchases', 'module': 'purchases',
             'description': 'القدرة على عرض المشتريات'},
            {'name': 'إضافة مشتريات', 'codename': 'add_purchases', 'module': 'purchases',
             'description': 'القدرة على إضافة فواتير شراء'},
            {'name': 'تعديل المشتريات', 'codename': 'change_purchases', 'module': 'purchases',
             'description': 'القدرة على تعديل المشتريات'},
            {'name': 'حذف المشتريات', 'codename': 'delete_purchases', 'module': 'purchases',
             'description': 'القدرة على حذف فواتير الشراء'},

            # صلاحيات التقارير
            {'name': 'عرض التقارير', 'codename': 'view_reports', 'module': 'reports',
             'description': 'القدرة على عرض التقارير'},
            {'name': 'تصدير التقارير', 'codename': 'export_reports', 'module': 'reports',
             'description': 'القدرة على تصدير التقارير'},

            # صلاحيات النظام
            {'name': 'إعدادات النظام', 'codename': 'system_settings', 'module': 'system',
             'description': 'القدرة على تعديل إعدادات النظام'},
        ]

        permissions = {}
        for data in permissions_data:
            permission, created = Permission.objects.get_or_create(
                codename=data['codename'],
                defaults=data
            )
            permissions[data['codename']] = permission
            if created:
                self.stdout.write(f'✅ تم إنشاء صلاحية: {data["name"]}')

        return permissions

    def create_roles(self, permissions):
        """إنشاء الأدوار الـ 6 وتعيين الصلاحيات المناسبة"""
        roles_data = [
            {
                'name': 'super_admin',
                'description': 'المدير العام يمتلك صلاحيات كاملة على النظام بما في ذلك إدارة جميع المستخدمين والأدوار وإعدادات النظام',
                'permissions': list(permissions.values())  # جميع الصلاحيات
            },
            {
                'name': 'admin',
                'description': 'مدير النظام يمكنه إدارة المستخدمين (عدا المدير العام) والمنتجات والمخازن والوصول لجميع التقارير',
                'permissions': [
                    permissions['view_users'], permissions['add_users'], permissions['change_users'],
                    permissions['delete_users'],
                    permissions['view_products'], permissions['add_products'], permissions['change_products'],
                    permissions['delete_products'],
                    permissions['view_inventory'], permissions['manage_inventory'], permissions['change_inventory'],
                    permissions['view_sales'], permissions['add_sales'], permissions['change_sales'],
                    permissions['delete_sales'],
                    permissions['view_purchases'], permissions['add_purchases'], permissions['change_purchases'],
                    permissions['delete_purchases'],
                    permissions['view_reports'], permissions['export_reports'],
                ]
            },
            {
                'name': 'inventory_manager',
                'description': 'مدير المخازن يمكنه إدارة المخزون والتحويلات ومراقبة مستويات المخزون وتنبيهات المخزون',
                'permissions': [
                    permissions['view_products'], permissions['view_inventory'], permissions['manage_inventory'],
                    permissions['change_inventory'],
                    permissions['view_reports'],
                ]
            },
            {
                'name': 'purchase_manager',
                'description': 'مدير المشتريات يمكنه إدارة فواتير الشراء والموردين وتقارير المشتريات',
                'permissions': [
                    permissions['view_products'], permissions['view_purchases'], permissions['add_purchases'],
                    permissions['change_purchases'], permissions['delete_purchases'],
                    permissions['view_inventory'], permissions['view_reports'], permissions['export_reports'],
                ]
            },
            {
                'name': 'sales_manager',
                'description': 'مدير المبيعات يمكنه إدارة فواتير البيع والعملاء وتقارير المبيعات',
                'permissions': [
                    permissions['view_products'], permissions['view_sales'], permissions['add_sales'],
                    permissions['change_sales'], permissions['delete_sales'],
                    permissions['view_inventory'], permissions['view_reports'], permissions['export_reports'],
                ]
            },
            {
                'name': 'viewer',
                'description': 'المشاهد يمكنه عرض البيانات فقط وتقارير القراءة فقط بدون إمكانية إجراء أي تعديلات',
                'permissions': [
                    permissions['view_users'], permissions['view_products'], permissions['view_inventory'],
                    permissions['view_sales'], permissions['view_purchases'], permissions['view_reports'],
                ]
            },
        ]

        roles = {}
        for data in roles_data:
            role, created = UserRole.objects.get_or_create(
                name=data['name'],
                defaults={'description': data['description']}
            )
            if created:
                role.permissions.set(data['permissions'])
                self.stdout.write(f'✅ تم إنشاء دور: {role.get_name_display()}')
            roles[data['name']] = role

        return roles

    def create_users(self, roles):
        """إنشاء مستخدمين افتراضيين بجميع الأدوار"""
        users_data = [
            # المدير العام
            {
                'email': 'superadmin@company.com',
                'first_name': 'أحمد',
                'last_name': 'الفهيد',
                'phone': '+966500000001',
                'department': 'الإدارة العليا',
                'role': roles['super_admin'],
                'password': 'SuperAdmin123!',
            },
            # مدير النظام
            {
                'email': 'admin@company.com',
                'first_name': 'محمد',
                'last_name': 'العلي',
                'phone': '+966500000002',
                'department': 'تقنية المعلومات',
                'role': roles['admin'],
                'password': 'Admin123!',
            },
            # مدير المخازن
            {
                'email': 'inventory@company.com',
                'first_name': 'خالد',
                'last_name': 'الزيد',
                'phone': '+966500000003',
                'department': 'المخازن',
                'role': roles['inventory_manager'],
                'password': 'Inventory123!',
            },
            # مدير المشتريات
            {
                'email': 'purchase@company.com',
                'first_name': 'سعيد',
                'last_name': 'الغامدي',
                'phone': '+966500000004',
                'department': 'المشتريات',
                'role': roles['purchase_manager'],
                'password': 'Purchase123!',
            },
            # مدير المبيعات
            {
                'email': 'sales@company.com',
                'first_name': 'فهد',
                'last_name': 'السعد',
                'phone': '+966500000005',
                'department': 'المبيعات',
                'role': roles['sales_manager'],
                'password': 'Sales123!',
            },
            # مشاهد
            {
                'email': 'viewer@company.com',
                'first_name': 'ناصر',
                'last_name': 'القحطاني',
                'phone': '+966500000006',
                'department': 'مراقبة الجودة',
                'role': roles['viewer'],
                'password': 'Viewer123!',
            },
            # مستخدمين إضافين لكل دور
            {
                'email': 'admin2@company.com',
                'first_name': 'عبدالله',
                'last_name': 'الرشيد',
                'phone': '+966500000007',
                'department': 'الدعم الفني',
                'role': roles['admin'],
                'password': 'Admin2123!',
            },
            {
                'email': 'inventory2@company.com',
                'first_name': 'تركي',
                'last_name': 'العبيد',
                'phone': '+966500000008',
                'department': 'المخازن',
                'role': roles['inventory_manager'],
                'password': 'Inventory2123!',
            },
            {
                'email': 'sales2@company.com',
                'first_name': 'بدر',
                'last_name': 'النجار',
                'phone': '+966500000009',
                'department': 'المبيعات',
                'role': roles['sales_manager'],
                'password': 'Sales2123!',
            },
            {
                'email': 'viewer2@company.com',
                'first_name': 'ماجد',
                'last_name': 'الحارثي',
                'phone': '+966500000010',
                'department': 'التدقيق',
                'role': roles['viewer'],
                'password': 'Viewer2123!',
            },
        ]

        CustomUser = get_user_model()

        for user_data in users_data:
            # التحقق إذا كان المستخدم موجود مسبقاً
            if not CustomUser.objects.filter(email=user_data['email']).exists():
                user = CustomUser.objects.create_user(
                    email=user_data['email'],
                    password=user_data['password'],
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name'],
                    phone=user_data['phone'],
                    department=user_data['department'],
                    role=user_data['role'],
                )
                user.is_active = True
                user.save()
                self.stdout.write(
                    f'✅ تم إنشاء مستخدم: {user.first_name} {user.last_name} ({user.role.get_name_display()})')
            else:
                self.stdout.write(f'⚠️  المستخدم موجود مسبقاً: {user_data["email"]}')

        self.stdout.write(
            self.style.SUCCESS(f'🎉 تم إنشاء {len(users_data)} مستخدم بنجاح!')
        )
