from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.urls import reverse_lazy
from django.db.models import Q, Count
from .models import CustomUser, UserRole, ActivityLog
from .forms import CustomUserCreationForm, CustomUserChangeForm, LoginForm
from .mixins import AdminRequiredMixin, SuperAdminRequiredMixin
from .utils import log_activity
from .decorators import role_required
from django.contrib.auth.views import PasswordChangeView, PasswordResetView, PasswordResetConfirmView
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import DeleteView


def custom_login(request):
    """
    تحكم في عملية تسجيل دخول المستخدمين.
    إذا كان المستخدم مسجلاً دخوله بالفعل، يتم توجيهه للوحة التحكم.
    """
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
    if request.user.is_authenticated:  # التحقق مما إذا كان المستخدم يمتلك جلسة نشطة بالفعل
        return redirect('accounts:dashboard')  # توجيهه للوحة التحكم لمنع الوصول لصفحة الدخول مرة أخرى

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
    if request.method == 'POST':  # معالجة بيانات نموذج الدخول عند إرسالها
        form = LoginForm(request.POST)  # تعبئة النموذج بالبيانات المرسلة
        if form.is_valid():  # التأكد من صحة تنسيق البريد الإلكتروني وكلمة المرور
            # استخراج البيانات النظيفة من النموذج
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            remember_me = form.cleaned_data['remember_me']
            email = form.cleaned_data['email']  # الحصول على البريد الإلكتروني الموثق
            password = form.cleaned_data['password']  # الحصول على كلمة المرور
            remember_me = form.cleaned_data['remember_me']  # التحقق من خيار البقاء متصلاً

            # التحقق من صحة بيانات الاعتماد
            user = authenticate(request, email=email, password=password)
            user = authenticate(request, email=email, password=password)  # استدعاء محرك المصادقة المخصص لفحص البيانات

            if user is not None:
                login(request, user)  # تسجيل الدخول في الجلسة (Session)
            if user is not None:  # في حال مطابقة البيانات لمستخدم موجود ونشط
                login(request, user)  # إنشاء جلسة عمل رسمية للمستخدم في النظام
                
                # إذا لم يختر المستخدم "تذكرني"، تنتهي الجلسة بإغلاق المتصفح
                if not remember_me:
                    request.session.set_expiry(0)
                if not remember_me:  # إذا لم يتم تفعيل خيار البقاء متصلاً
                    request.session.set_expiry(0)  # ضبط صلاحية الجلسة لتنتهي فور إغلاق نافذة المتصفح

                # تسجيل النشاط في سجل الأنشطة للرقابة
                log_activity(user, 'تسجيل دخول', 'CustomUser', user.id,
                             {'email': user.email}, request)
                messages.success(request, f'مرحباً بعودتك {user.first_name}!')
                log_activity(user, 'تسجيل دخول', 'CustomUser', user.id,  # تدوين عملية الدخول في السجل الأمني
                             {'email': user.email}, request)  # إضافة تفاصيل البريد وعنوان IP
                messages.success(request, f'مرحباً بعودتك {user.first_name}!')  # عرض رسالة ترحيبية

                # التوجيه للصفحة التي كان يحاول الوصول إليها أو للوحة التحكم
                next_url = request.GET.get('next')
                if next_url:
                    return redirect(next_url)
                return redirect('accounts:dashboard')
                next_url = request.GET.get('next')  # جلب الرابط الذي حاول المستخدم الوصول إليه قبل تسجيل الدخول
                if next_url:  # إذا كان هناك رابط مخزن
                    return redirect(next_url)  # إعادة توجيهه للرابط الأصلي
                return redirect('accounts:dashboard')  # وإلا التوجه للوحة التحكم الافتراضية
            else:
                messages.error(request, 'البريد الإلكتروني أو كلمة المرور غير صحيحة.')
                messages.error(request, 'البريد الإلكتروني أو كلمة المرور غير صحيحة.')  # إظهار خطأ في حال فشل المصادقة
    else:
        form = LoginForm()
        form = LoginForm()  # عرض نموذج فارغ في حالة طلب الصفحة عبر GET

    return render(request, 'accounts/auth/login.html', {'form': form})


def custom_logout(request):
    """
    تسجيل خروج المستخدم وإنهاء الجلسة الحالية.
    """
    if request.user.is_authenticated:
    if request.user.is_authenticated:  # التحقق من أن هناك مستخدم مسجل بالفعل
        # تسجيل عملية الخروج في السجل قبل إنهاء الجلسة
        log_activity(request.user, 'تسجيل خروج', 'CustomUser', request.user.id,
                     {'email': request.user.email}, request)
    logout(request)
    messages.success(request, 'تم تسجيل الخروج بنجاح.')
    return redirect('accounts:login')
        log_activity(request.user, 'تسجيل خروج', 'CustomUser', request.user.id,  # توثيق وقت خروج المستخدم
                     {'email': request.user.email}, request)  # أرشفة البيانات قبل مسح الجلسة
    logout(request)  # تدمير بيانات الجلسة (Session) نهائياً
    messages.success(request, 'تم تسجيل الخروج بنجاح.')  # رسالة تأكيد الخروج
    return redirect('accounts:login')  # إعادة التوجيه لصفحة تسجيل الدخول


from django.db.models import Sum
from sales.models import SalesInvoice, Customer
from purchases.models import PurchaseOrder, Supplier
from inventory.models import StockAlert, Warehouse
from products.models import Product

@login_required
def dashboard(request):
    """
    لوحة تحكم عمليات المستودع.
    تقوم بجمع إحصائيات مالية وعددية وتنبيهات المخزون لعرضها بشكل ملخص.
    """
    # حساب الإجماليات المالية للمبيعات المدفوعة والمشتريات المكتملة
    total_sales = SalesInvoice.objects.filter(status='paid').aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    total_purchases = PurchaseOrder.objects.filter(status='completed').aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    
    # حساب أعداد الكيانات النشطة في النظام
    product_count = Product.objects.filter(is_active=True).count()
    customer_count = Customer.objects.filter(is_active=True).count()
    supplier_count = Supplier.objects.filter(is_active=True).count()
    warehouse_count = Warehouse.objects.filter(is_active=True).count()
    
    # جلب التنبيهات التي لم يتم حلها بعد
    unresolved_alerts = StockAlert.objects.filter(is_resolved=False)
    total_alerts = unresolved_alerts.count()
    
    # تصنيف التنبيهات (نقص مخزون أو انتهاء صلاحية)
    low_stock_alerts = unresolved_alerts.filter(alert_type='low_stock').count()
    expiry_alerts = unresolved_alerts.filter(alert_type='expiry').count()
    
    # جلب آخر العمليات والتنبيهات لعرضها في جداول مختصرة
    recent_invoices = SalesInvoice.objects.order_by('-created_at')[:5]
    recent_purchases = PurchaseOrder.objects.order_by('-created_at')[:5]
    recent_alerts = unresolved_alerts.order_by('-created_at')[:5]

    context = {
        'total_sales': total_sales,
        'total_purchases': total_purchases,
        'product_count': product_count,
        'customer_count': customer_count,
        'supplier_count': supplier_count,
        'warehouse_count': warehouse_count,
        'total_alerts': total_alerts,
        'low_stock_alerts': low_stock_alerts,
        'expiry_alerts': expiry_alerts,
        'recent_invoices': recent_invoices,
        'recent_purchases': recent_purchases,
        'recent_alerts': recent_alerts,
    }
    return render(request, 'accounts/dashboard.html', context)


@login_required
@role_required(['admin', 'super_admin'])
def user_dashboard(request):
    """
    لوحة تحكم إدارة المستخدمين (للمديرين فقط).
    تعرض إحصائيات حول أعداد المستخدمين وتوزيع الأدوار وآخر الأنشطة في النظام.
    """
    # إحصائيات عامة حول المستخدمين
    total_users = CustomUser.objects.count()
    active_users = CustomUser.objects.filter(is_active=True).count()
    
    # توزيع الأدوار (كم مستخدم في كل دور) باستخدام التجميع (Aggregation)
    role_distribution = UserRole.objects.annotate(user_count=Count('customuser'))
    
    # جلب آخر 20 نشاط قام به المستخدمون في النظام للرقابة
    all_activities = ActivityLog.objects.select_related('user').order_by('-timestamp')[:20]
    
    # جلب آخر 5 مستخدمين تم تسجيلهم
    recent_users = CustomUser.objects.order_by('-date_joined')[:5]

    context = {
        'total_users': total_users,
        'active_users': active_users,
        'role_distribution': role_distribution,
        'all_activities': all_activities,
        'recent_users': recent_users,
    }
    return render(request, 'accounts/users/dashboard.html', context)

class UserListView(AdminRequiredMixin, ListView):
    """
    عرض قائمة المستخدمين مع إمكانيات البحث والتصنيف (Filtering).
    """
    model = CustomUser
    template_name = 'accounts/users/list.html'
    context_object_name = 'users'
    paginate_by = 10  # عرض 10 مستخدمين في كل صفحة

    def get_queryset(self):
        # البدء بجلب كافة المستخدمين
        queryset = CustomUser.objects.all()

        # البحث بالاسم أو البريد أو القسم إذا تم تزويد كلمة بحث
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(email__icontains=search) |
                Q(department__icontains=search)
            )

        # التصنيف حسب الدور (Role)
        role = self.request.GET.get('role')
        if role:
            queryset = queryset.filter(role__name=role)

        # التصنيف حسب الحالة (نشط / معطل)
        status = self.request.GET.get('status')
        if status == 'active':
            queryset = queryset.filter(is_active=True)
        elif status == 'inactive':
            queryset = queryset.filter(is_active=False)

        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        # إضافة قائمة الأدوار للسياق لاستخدامها في قائمة التصنيف المنسدلة
        context = super().get_context_data(**kwargs)
        context['roles'] = UserRole.objects.all()
        return context


class UserCreateView(AdminRequiredMixin, CreateView):
    """
    نماذج إنشاء مستخدم جديد في النظام.
    """
    model = CustomUser
    form_class = CustomUserCreationForm
    template_name = 'accounts/users/create.html'
    success_url = reverse_lazy('accounts:user_list')

    def form_valid(self, form):
        # استدعاء الدالة الأصلية لحفظ المستخدم
        response = super().form_valid(form)
        
        # تسجيل عملية الإنشاء في سجل الأنشطة
        log_activity(self.request.user, 'إنشاء مستخدم', 'CustomUser',
                     self.object.id, {'email': self.object.email}, self.request)
        messages.success(self.request, 'تم إنشاء المستخدم بنجاح.')
        return response


class UserUpdateView(AdminRequiredMixin, UpdateView):
    """
    نماذج تحديث بيانات مستخدم موجود بالفعل.
    """
    model = CustomUser
    form_class = CustomUserChangeForm
    template_name = 'accounts/users/update.html'
    success_url = reverse_lazy('accounts:user_list')

    def form_valid(self, form):
        # استدعاء الدالة الأصلية لحفظ التعديلات
        response = super().form_valid(form)
        
        # تسجيل عملية التحديث في السجل
        log_activity(self.request.user, 'تحديث مستخدم', 'CustomUser',
                     self.object.id, {'email': self.object.email}, self.request)
        messages.success(self.request, 'تم تحديث بيانات المستخدم بنجاح.')
        return response


@login_required
def user_profile(request):
    """
    عرض وتعديل الملف الشخصي للمستخدم الحالي.
    """
    user = request.user
    # جلب آخر 5 أنشطة قام بها هذا المستخدم تحديداً
    recent_activities = ActivityLog.objects.filter(user=user)[:5]

    if request.method == 'POST':
        # معالجة طلب التعديل
        form = CustomUserChangeForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تحديث الملف الشخصي بنجاح.')
            return redirect('accounts:profile')
    else:
        # عرض البيانات الحالية
        form = CustomUserChangeForm(instance=user)

    context = {
        'form': form,
        'recent_activities': recent_activities,
    }
    return render(request, 'accounts/users/profile.html', context)


class RoleListView(SuperAdminRequiredMixin, ListView):
    """
    عرض قائمة أدوار المستخدمين (للمدير العام فقط).
    """
    model = UserRole
    template_name = 'accounts/roles/list.html'
    context_object_name = 'roles'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # حساب عدد المستخدمين المنتمين لكل دور لعرضه في الواجهة
        for role in context['roles']:
            role.user_count = CustomUser.objects.filter(role=role).count()
        return context


class ActivityLogListView(AdminRequiredMixin, ListView):
    """
    صفحة مخصصة لعرض سجلات الأنشطة مع خيارات تصفية متقدمة.
    """
    model = ActivityLog
    template_name = 'accounts/activity/logs.html'
    context_object_name = 'activities'
    paginate_by = 20

    def get_queryset(self):
        # جلب كافة السجلات بشكل افتراضي
        queryset = ActivityLog.objects.all()

        # التصفية حسب مستخدم معين
        user_id = self.request.GET.get('user')
        if user_id:
            queryset = queryset.filter(user_id=user_id)

        # التصفية حسب نوع الإجراء المكتوب في حقل البحث
        action = self.request.GET.get('action')
        if action:
            queryset = queryset.filter(action__icontains=action)

        # التصفية حسب نطاق زمني (تاريخ البداية والنهاية)
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')
        if date_from:
            queryset = queryset.filter(timestamp__date__gte=date_from)
        if date_to:
            queryset = queryset.filter(timestamp__date__lte=date_to)

        return queryset.order_by('-timestamp')

    def get_context_data(self, **kwargs):
        # جلب قائمة المستخدمين لعرضهم في فلتر "المستخدم"
        context = super().get_context_data(**kwargs)
        context['users'] = CustomUser.objects.all()
        return context


# Add these views to your existing views

class CustomPasswordChangeView(SuccessMessageMixin, PasswordChangeView):
    """
    تغيير كلمة المرور من داخل الملف الشخصي.
    """
    template_name = 'accounts/auth/password_change.html'
    success_url = reverse_lazy('accounts:profile')
    success_message = 'تم تغيير كلمة المرور بنجاح'


class CustomPasswordResetView(SuccessMessageMixin, PasswordResetView):
    """
    بدء عملية استعادة كلمة المرور في حال نسيانها (إرسال بريد إلكتروني).
    """
    template_name = 'accounts/auth/password_reset.html'
    email_template_name = 'accounts/auth/password_reset_email.html'
    success_url = reverse_lazy('accounts:login')
    success_message = 'تم إرسال رابط استعادة كلمة المرور إلى بريدك الإلكتروني'


class CustomPasswordResetConfirmView(SuccessMessageMixin, PasswordResetConfirmView):
    """
    تأكيد تعيين كلمة المرور الجديدة عبر الرابط المرسل بالبريد.
    """
    template_name = 'accounts/auth/password_reset_confirm.html'
    success_url = reverse_lazy('accounts:login')
    success_message = 'تم إعادة تعيين كلمة المرور بنجاح'


class UserDeleteView(AdminRequiredMixin, DeleteView):
    """
    حذف مستخدم من النظام.
    """
    model = CustomUser
    template_name = 'accounts/users/confirm_delete.html'
    success_url = reverse_lazy('accounts:user_list')

    def delete(self, request, *args, **kwargs):
        user = self.get_object()
        # تسجيل عملية الحذف قبل التنفيذ الفعلي
        log_activity(request.user, 'حذف مستخدم', 'CustomUser', user.id,
                     {'email': user.email}, request)
        messages.success(request, 'تم حذف المستخدم بنجاح.')
        return super().delete(request, *args, **kwargs)


class UserDetailView(AdminRequiredMixin, DetailView):
    """
    عرض التفاصيل الكاملة لمستنخدم معين.
    """
    model = CustomUser
    template_name = 'accounts/users/detail.html'
    context_object_name = 'user_obj'


class RoleCreateView(SuperAdminRequiredMixin, CreateView):
    """
    إنشاء دور جديد (Role) في النظام.
    """
    model = UserRole
    template_name = 'accounts/roles/create.html'
    fields = ['name', 'description', 'permissions']
    success_url = reverse_lazy('accounts:role_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        # تسجيل عملية إنشاء الدور
        log_activity(self.request.user, 'إنشاء دور', 'UserRole',
                     self.object.id, {'name': self.object.name}, self.request)
        messages.success(self.request, 'تم إنشاء الدور بنجاح.')
        return response


class RoleUpdateView(SuperAdminRequiredMixin, UpdateView):
    """
    تحديث بيانات وصف الدور.
    """
    model = UserRole
    template_name = 'accounts/roles/update.html'
    fields = ['name', 'description', 'permissions']
    success_url = reverse_lazy('accounts:role_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        # تسجيل عملية تحديث الدور
        log_activity(self.request.user, 'تحديث دور', 'UserRole',
                     self.object.id, {'name': self.object.name}, self.request)
        messages.success(self.request, 'تم تحديث الدور بنجاح.')
        return response


@login_required
@role_required(['super_admin'])
def role_permissions(request, pk):
    """
    إدارة الصلاحيات الممنوحة لدور معين.
    تعرض كافة الصلاحيات مقسمة حسب الوحدات (Modules).
    """
    role = get_object_or_404(UserRole, pk=pk)
    permissions = Permission.objects.all()
    permissions_by_module = {}

    # تجميع الصلاحيات في مجموعات حسب الوحدة (Module) لتنظيم العرض
    for permission in permissions:
        module = permission.module
        if module not in permissions_by_module:
            permissions_by_module[module] = []
        permissions_by_module[module].append(permission)

    if request.method == 'POST':
        # استقبال قائمة الصلاحيات المختارة وربطها بالدور
        selected_permissions = request.POST.getlist('permissions')
        role.permissions.set(selected_permissions)

        # تسجيل تحديث الصلاحيات
        log_activity(request.user, 'تحديث صلاحيات الدور', 'UserRole',
                     role.id, {'name': role.name, 'permissions_count': len(selected_permissions)}, request)
        messages.success(request, 'تم تحديث صلاحيات الدور بنجاح.')
        return redirect('accounts:role_list')

    context = {
        'role': role,
        'permissions_by_module': permissions_by_module,
    }
    return render(request, 'accounts/roles/permissions.html', context)


class ActivityDetailView(AdminRequiredMixin, DetailView):
    model = ActivityLog
    template_name = 'accounts/activity/detail.html'
    context_object_name = 'activity'
