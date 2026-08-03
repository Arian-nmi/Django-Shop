from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from order.models import UserAddressModel
from accounts.models import Profile


class UserAddressForm(forms.ModelForm):
    class Meta:
        model = UserAddressModel

        fields = [
            "address",
            "state",
            "city",
            "zip_code",
        ]

        widgets = {
            "address": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "آدرس کامل",
                }
            ),
            "state": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "استان",
                }
            ),
            "city": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "شهر",
                }
            ),
            "zip_code": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "کد پستی",
                }
            ),
        }


class CustomerProfileForm(forms.ModelForm):
    class Meta:
        model = Profile

        fields = [
            "first_name",
            "last_name",
            "phone_number",
        ]

        widgets = {
            "first_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "نام",
                }
            ),
            "last_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "نام خانوادگی",
                }
            ),
            "phone_number": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "شماره موبایل",
                }
            ),
        }


class CustomerPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["old_password"].widget.attrs.update(
            {
                "class": "form-control",
                "placeholder": "رمز عبور فعلی",
            }
        )

        self.fields["new_password1"].widget.attrs.update(
            {
                "class": "form-control",
                "placeholder": "رمز عبور جدید",
            }
        )

        self.fields["new_password2"].widget.attrs.update(
            {
                "class": "form-control",
                "placeholder": "تکرار رمز عبور جدید",
            }
        )