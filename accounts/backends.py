from django.contrib.auth.backends import ModelBackend
from .models import CustomUser

class CustomAuthBackend(ModelBackend):
    def authenticate(self, request, email=None, password=None, **kwargs):
        try:
            user = CustomUser.objects.get(email=email)
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
        except CustomUser.DoesNotExist:
            return None
        return None

    def user_can_authenticate(self, user):
        return user.is_active