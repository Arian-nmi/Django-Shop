from django.contrib.auth import forms as auth_forms
from django.contrib.auth.forms import UserCreationForm
from .models import User


class AuthenticationForm(auth_forms.AuthenticationForm):
    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)


class SignUpForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("email",)