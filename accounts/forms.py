from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser, UserRole


class CustomUserCreationForm(UserCreationForm):
    """
    نموذج مخصص لإنشاء مستخدمين جدد عبر واجهة الإدارة.
    يتضمن تأكيد كلمة المرور وحقول إضافية مثل الهاتف والقسم.
    """
    password1 = forms.CharField(
        label="كلمة المرور",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    password2 = forms.CharField(
        label="تأكيد كلمة المرور",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = CustomUser
        # تحديد الحقول التي ستظهر في النموذج
        fields = ('email', 'first_name', 'last_name', 'phone', 'department', 'role')
        # إضافة تنسيقات CSS لربط الحقول بتصميم Bootstrap
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'department': forms.TextInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-control'}),
        }
        # تعيين الأسماء المعروضة للحقول باللغة العربية
        labels = {
            'email': 'البريد الإلكتروني',
            'first_name': 'الاسم الأول',
            'last_name': 'الاسم الأخير',
            'phone': 'رقم الهاتف',
            'department': 'القسم',
            'role': 'الدور',
        }


class CustomUserChangeForm(UserChangeForm):
    """
    نموذج لتعديل بيانات مستخدم موجود مع إمكانية تفعيل أو تعطيل الحساب.
    """
    class Meta:
        model = CustomUser
        fields = ('email', 'first_name', 'last_name', 'phone', 'department', 'role', 'is_active')
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'department': forms.TextInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class LoginForm(forms.Form):
    """
    نموذج بسيط للتحقق من بيانات الدخول (البريد الإلكتروني وكلمة المرور).
    لا يرتبط بموديل معين بشكل مباشر ولكنه يستخدم للتحقق الأولي من المدخلات.
    """
    email = forms.EmailField(
        label="البريد الإلكتروني",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'أدخل بريدك الإلكتروني'})
    )
    password = forms.CharField(
        label="كلمة المرور",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'أدخل كلمة المرور'})
    )
    remember_me = forms.BooleanField(
        required=False,
        label="تذكرني",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
