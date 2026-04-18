from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.urls import reverse_lazy
from django.db.models import Q
from .models import CustomUser, UserRole, ActivityLog
from .forms import CustomUserCreationForm, CustomUserChangeForm, LoginForm
from .mixins import AdminRequiredMixin, SuperAdminRequiredMixin
from .utils import log_activity
from .decorators import role_required
from django.contrib.auth.views import PasswordChangeView, PasswordResetView, PasswordResetConfirmView
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import DeleteView


def custom_login(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            remember_me = form.cleaned_data['remember_me']

            user = authenticate(request, email=email, password=password)

            if user is not None:
                login(request, user)
                if not remember_me:
                    request.session.set_expiry(0)

                log_activity(user, 'تسجيل دخول', 'CustomUser', user.id,
                             {'email': user.email}, request)
                messages.success(request, f'مرحباً بعودتك {user.first_name}!')

                next_url = request.GET.get('next')
                if next_url:
                    return redirect(next_url)
                return redirect('accounts:dashboard')
            else:
                messages.error(request, 'البريد الإلكتروني أو كلمة المرور غير صحيحة.')
    else:
        form = LoginForm()

    return render(request, 'accounts/auth/login.html', {'form': form})


def custom_logout(request):
    if request.user.is_authenticated:
        log_activity(request.user, 'تسجيل خروج', 'CustomUser', request.user.id,
                     {'email': request.user.email}, request)
    logout(request)
    messages.success(request, 'تم تسجيل الخروج بنجاح.')
    return redirect('accounts:login')


@login_required
def dashboard(request):
    # إحصائيات المستخدمين
    total_users = CustomUser.objects.count()
    active_users = CustomUser.objects.filter(is_active=True).count()
    
    # توزيع المستخدمين حسب الأدوار
    role_distribution = UserRole.objects.annotate(user_count=Count('customuser'))
    
    # آخر النشاطات (لجميع المستخدمين)
    all_activities = ActivityLog.objects.select_related('user').order_by('-timestamp')[:20]
    
    # آخر مستخدمين مسجلين
    recent_users = CustomUser.objects.order_by('-date_joined')[:5]

    context = {
        'total_users': total_users,
        'active_users': active_users,
        'role_distribution': role_distribution,
        'all_activities': all_activities,
        'recent_users': recent_users,
    }
    return render(request, 'accounts/dashboard.html', context)


class UserListView(AdminRequiredMixin, ListView):
    model = CustomUser
    template_name = 'accounts/users/list.html'
    context_object_name = 'users'
    paginate_by = 10

    def get_queryset(self):
        queryset = CustomUser.objects.all()

        # Search
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(email__icontains=search) |
                Q(department__icontains=search)
            )

        # Filter by role
        role = self.request.GET.get('role')
        if role:
            queryset = queryset.filter(role__name=role)

        # Filter by status
        status = self.request.GET.get('status')
        if status == 'active':
            queryset = queryset.filter(is_active=True)
        elif status == 'inactive':
            queryset = queryset.filter(is_active=False)

        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['roles'] = UserRole.objects.all()
        return context


class UserCreateView(AdminRequiredMixin, CreateView):
    model = CustomUser
    form_class = CustomUserCreationForm
    template_name = 'accounts/users/create.html'
    success_url = reverse_lazy('accounts:user_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        log_activity(self.request.user, 'إنشاء مستخدم', 'CustomUser',
                     self.object.id, {'email': self.object.email}, self.request)
        messages.success(self.request, 'تم إنشاء المستخدم بنجاح.')
        return response


class UserUpdateView(AdminRequiredMixin, UpdateView):
    model = CustomUser
    form_class = CustomUserChangeForm
    template_name = 'accounts/users/update.html'
    success_url = reverse_lazy('accounts:user_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        log_activity(self.request.user, 'تحديث مستخدم', 'CustomUser',
                     self.object.id, {'email': self.object.email}, self.request)
        messages.success(self.request, 'تم تحديث بيانات المستخدم بنجاح.')
        return response


@login_required
def user_profile(request):
    user = request.user
    recent_activities = ActivityLog.objects.filter(user=user)[:5]

    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تحديث الملف الشخصي بنجاح.')
            return redirect('accounts:profile')
    else:
        form = CustomUserChangeForm(instance=user)

    context = {
        'form': form,
        'recent_activities': recent_activities,
    }
    return render(request, 'accounts/users/profile.html', context)


class RoleListView(SuperAdminRequiredMixin, ListView):
    model = UserRole
    template_name = 'accounts/roles/list.html'
    context_object_name = 'roles'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add user count for each role
        for role in context['roles']:
            role.user_count = CustomUser.objects.filter(role=role).count()
        return context


class ActivityLogListView(AdminRequiredMixin, ListView):
    model = ActivityLog
    template_name = 'accounts/activity/logs.html'
    context_object_name = 'activities'
    paginate_by = 20

    def get_queryset(self):
        queryset = ActivityLog.objects.all()

        # Filter by user
        user_id = self.request.GET.get('user')
        if user_id:
            queryset = queryset.filter(user_id=user_id)

        # Filter by action
        action = self.request.GET.get('action')
        if action:
            queryset = queryset.filter(action__icontains=action)

        # Filter by date
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')
        if date_from:
            queryset = queryset.filter(timestamp__date__gte=date_from)
        if date_to:
            queryset = queryset.filter(timestamp__date__lte=date_to)

        return queryset.order_by('-timestamp')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['users'] = CustomUser.objects.all()
        return context


# Add these views to your existing views

class CustomPasswordChangeView(SuccessMessageMixin, PasswordChangeView):
    template_name = 'accounts/auth/password_change.html'
    success_url = reverse_lazy('accounts:profile')
    success_message = 'تم تغيير كلمة المرور بنجاح'


class CustomPasswordResetView(SuccessMessageMixin, PasswordResetView):
    template_name = 'accounts/auth/password_reset.html'
    email_template_name = 'accounts/auth/password_reset_email.html'
    success_url = reverse_lazy('accounts:login')
    success_message = 'تم إرسال رابط استعادة كلمة المرور إلى بريدك الإلكتروني'


class CustomPasswordResetConfirmView(SuccessMessageMixin, PasswordResetConfirmView):
    template_name = 'accounts/auth/password_reset_confirm.html'
    success_url = reverse_lazy('accounts:login')
    success_message = 'تم إعادة تعيين كلمة المرور بنجاح'


class UserDeleteView(AdminRequiredMixin, DeleteView):
    model = CustomUser
    template_name = 'accounts/users/confirm_delete.html'
    success_url = reverse_lazy('accounts:user_list')

    def delete(self, request, *args, **kwargs):
        user = self.get_object()
        log_activity(request.user, 'حذف مستخدم', 'CustomUser', user.id,
                     {'email': user.email}, request)
        messages.success(request, 'تم حذف المستخدم بنجاح.')
        return super().delete(request, *args, **kwargs)


class UserDetailView(AdminRequiredMixin, DetailView):
    model = CustomUser
    template_name = 'accounts/users/detail.html'
    context_object_name = 'user_obj'


class RoleCreateView(SuperAdminRequiredMixin, CreateView):
    model = UserRole
    template_name = 'accounts/roles/create.html'
    fields = ['name', 'description', 'permissions']
    success_url = reverse_lazy('accounts:role_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        log_activity(self.request.user, 'إنشاء دور', 'UserRole',
                     self.object.id, {'name': self.object.name}, self.request)
        messages.success(self.request, 'تم إنشاء الدور بنجاح.')
        return response


class RoleUpdateView(SuperAdminRequiredMixin, UpdateView):
    model = UserRole
    template_name = 'accounts/roles/update.html'
    fields = ['name', 'description', 'permissions']
    success_url = reverse_lazy('accounts:role_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        log_activity(self.request.user, 'تحديث دور', 'UserRole',
                     self.object.id, {'name': self.object.name}, self.request)
        messages.success(self.request, 'تم تحديث الدور بنجاح.')
        return response


@login_required
@role_required(['super_admin'])
def role_permissions(request, pk):
    role = get_object_or_404(UserRole, pk=pk)
    permissions = Permission.objects.all()
    permissions_by_module = {}

    for permission in permissions:
        module = permission.module
        if module not in permissions_by_module:
            permissions_by_module[module] = []
        permissions_by_module[module].append(permission)

    if request.method == 'POST':
        selected_permissions = request.POST.getlist('permissions')
        role.permissions.set(selected_permissions)

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
