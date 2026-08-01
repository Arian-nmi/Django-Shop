from django import forms
from order.models import UserAddressModel


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