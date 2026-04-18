# تعطيل/إعادة تشغيل المصادقة

## الحالة الحالية
تم تعطيل نظام المصادقة مؤقتاً للسماح بالدخول المباشر إلى النظام دون الحاجة لتسجيل الدخول.

## كيفية إعادة تشغيل المصادقة

لإعادة تشغيل نظام المصادقة، اتبع الخطوات التالية:

### 1. تعديل `products/views.py`

أعد إضافة `@login_required` إلى جميع الدوال في الملف. يمكنك استخدام الكود التالي:

```python
# قم بتشغيل هذا السكريبت لإعادة @login_required
import re

content = open('products/views.py', 'r', encoding='utf-8').read()

# إعادة إضافة @login_required قبل كل دالة
content = re.sub(
    r'(\n)(def \w+\()',
    r'\1@login_required\n\1\2',
    content
)

# التأكد من أن import موجود
if 'from django.contrib.auth.decorators import login_required' not in content:
    content = content.replace(
        '# from django.contrib.auth.decorators import login_required  # معطل مؤقتاً',
        'from django.contrib.auth.decorators import login_required'
    )

open('products/views.py', 'w', encoding='utf-8').write(content)
print('تمت إعادة @login_required إلى جميع الدوال')
```

### 2. تعديل `accounts/urls.py`

أعد السطر التالي إلى حالته الأصلية:

```python
# غير هذا السطر:
path('login/', views.custom_login, name='login'),

# إلى:
path('', views.custom_login, name='login'),
```

### 3. تعديل `warehouse_system/urls.py`

أعد السطر التالي إلى حالته الأصلية:

```python
# غير هذا السطر:
path('accounts/', include('accounts.urls')),

# إلى:
path('', include('accounts.urls')),
```

### 4. تعديل `warehouse_system/settings.py`

أعد تفعيل `LOGIN_URL`:

```python
# غير هذا السطر:
# LOGIN_URL = 'accounts:login'  # معطل مؤقتاً

# إلى:
LOGIN_URL = 'accounts:login'
```

### 5. إعادة تشغيل الخادم

بعد إجراء التعديلات، أعد تشغيل خادم Django:

```bash
py -3.10 manage.py runserver
```

## ملاحظات مهمة

- **كلمات المرور**: كلمات المرور مشفرة في قاعدة البيانات ولا يمكن قراءتها
- **المستخدمين المتاحين**: يمكنك رؤية قائمة المستخدمين في ملف `users_list.txt`
- **إنشاء مستخدم جديد**: استخدم `py -3.10 manage.py createsuperuser` لإنشاء مدير جديد

## قائمة المستخدمين الحاليين مع كلمات المرور

تم تعيين كلمات مرور بسيطة حسب الدور لتسهيل تجربة النظام:

| البريد الإلكتروني | الدور | القسم | كلمة المرور |
|-------------------|-------|-------|------------|
| aqeel@mangement.com | super_admin | الإدارة العليا | super123 |
| sa@gmail.com | super_admin | الادارة العليا | super123 |
| admin@company.com | admin | تقنية المعلومات | admin123 |
| admin2@company.com | admin | الدعم الفني | admin123 |
| inventory@company.com | inventory_manager | المخازن | inventory123 |
| inventory2@company.com | inventory_manager | المخازن | inventory123 |
| sales@company.com | sales_manager | المبيعات | sales123 |
| sales2@company.com | sales_manager | المبيعات | sales123 |
| mo@gmail.com | sales_manager | المبيعات | sales123 |
| purchase@company.com | purchase_manager | المشتريات | purchase123 |
| viewer@company.com | viewer | مراقبة الجودة (غير نشط) | viewer123 |

### كلمات المرور حسب الدور:
- **المدير العام (super_admin)**: `super123`
- **مدير النظام (admin)**: `admin123`
- **مدير المخازن (inventory_manager)**: `inventory123`
- **مدير المشتريات (purchase_manager)**: `purchase123`
- **مدير المبيعات (sales_manager)**: `sales123`
- **مشاهد (viewer)**: `viewer123`

**ملاحظة**: يمكنك تغيير كلمات المرور من لوحة التحكم بعد تسجيل الدخول.
