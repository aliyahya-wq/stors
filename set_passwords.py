#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
سكريبت لتعيين كلمات مرور بسيطة لجميع المستخدمين لتجربة النظام
"""

import os
import sys
import django

# إضافة مسار المشروع إلى Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# إعداد Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'warehouse_system.settings')
django.setup()

from accounts.models import CustomUser

def main():
    # قاموس الأدوار وكلمات المرور المقترحة
    role_passwords = {
        'super_admin': 'super123',
        'admin': 'admin123',
        'inventory_manager': 'inventory123',
        'purchase_manager': 'purchase123',
        'sales_manager': 'sales123',
        'viewer': 'viewer123',
    }
    
    # جلب جميع المستخدمين
    users = CustomUser.objects.all()
    
    if not users.exists():
        print("لا يوجد مستخدمين في قاعدة البيانات.")
        return
    
    print("=" * 80)
    print("تم تعيين كلمات المرور التالية:")
    print("=" * 80)
    print()
    
    output_file = 'users_list.txt'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("قائمة المستخدمين المسجلين في قاعدة البيانات مع كلمات المرور\n")
        f.write("=" * 80 + "\n\n")
        
        for user in users:
            # تحديد كلمة المرور حسب الدور
            role_name = user.role.name if user.role else 'unknown'
            password = role_passwords.get(role_name, 'user123')
            
            # تعيين كلمة المرور
            user.set_password(password)
            user.save()
            
            # كتابة المعلومات
            f.write(f"المستخدم: {user.get_full_name() or 'غير محدد'}\n")
            f.write("-" * 40 + "\n")
            f.write(f"الاسم الأول: {user.first_name or 'غير محدد'}\n")
            f.write(f"الاسم الأخير: {user.last_name or 'غير محدد'}\n")
            f.write(f"البريد الإلكتروني: {user.email}\n")
            f.write(f"كلمة المرور: {password}\n")
            f.write(f"الهاتف: {user.phone or 'غير محدد'}\n")
            f.write(f"القسم: {user.department or 'غير محدد'}\n")
            f.write(f"الدور: {role_name}\n")
            f.write(f"الحالة: {'نشط' if user.is_active else 'غير نشط'}\n")
            f.write(f"تاريخ الإنشاء: {user.date_joined.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("\n")
            
            print(f"• {user.get_full_name():20} | {user.email:30} | كلمة المرور: {password}")
        
        f.write(f"إجمالي المستخدمين: {users.count()}\n")
        f.write("=" * 80 + "\n")
        f.write("\nملاحظة: جميع كلمات المرور مؤقتة. يمكنك تغييرها من لوحة التحكم.\n")
    
    print()
    print(f"تم حفظ القائمة في الملف: {output_file}")
    print()
    print("=" * 80)
    print("كلمات المرور حسب الدور:")
    print("=" * 80)
    for role, password in role_passwords.items():
        role_arabic = {
            'super_admin': 'المدير العام',
            'admin': 'مدير النظام',
            'inventory_manager': 'مدير المخازن',
            'purchase_manager': 'مدير المشتريات',
            'sales_manager': 'مدير المبيعات',
            'viewer': 'مشاهد',
        }.get(role, role)
        print(f"  {role_arabic:20} ({role:20}): {password}")

if __name__ == '__main__':
    main()