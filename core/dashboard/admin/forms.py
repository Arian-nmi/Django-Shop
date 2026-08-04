from django import forms
from shop.models import ProductImageModel, ProductModel
from order.models import CouponModel


class AdminProductForm(forms.ModelForm):
    class Meta:
        model = ProductModel

        fields = [
            "category",
            "title",
            "slug",
            "image",
            "description",
            "brief_description",
            "stock",
            "status",
            "price",
            "discount_percent",
        ]

        widgets = {
            "category": forms.SelectMultiple(
                attrs={
                    "class": "form-select",
                }
            ),
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),
            "slug": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),
            "image": forms.ClearableFileInput(
                attrs={
                    "class": "form-control",
                    "accept": "image/png,image/jpeg,image/jpg",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 6,
                }
            ),
            "brief_description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                }
            ),
            "stock": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 0,
                }
            ),
            "status": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "price": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 0,
                }
            ),
            "discount_percent": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 0,
                    "max": 100,
                }
            ),
        }


class AdminProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImageModel

        fields = [
            "file",
        ]

        widgets = {
            "file": forms.ClearableFileInput(
                attrs={
                    "class": "form-control",
                    "accept": "image/png,image/jpeg,image/jpg",
                }
            ),
        }


class AdminCouponForm(forms.ModelForm):
    expiration_date = forms.DateTimeField(
        required=False,
        input_formats=[
            "%Y-%m-%dT%H:%M",
        ],
        widget=forms.DateTimeInput(
            format="%Y-%m-%dT%H:%M",
            attrs={
                "class": "form-control",
                "type": "datetime-local",
            },
        ),
    )
    class Meta:
        model = CouponModel

        fields = [
            "code",
            "discount_percent",
            "max_limit_usage",
            "expiration_date",
        ]

        widgets = {
            "code": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "مثلاً SUMMER10",
                }
            ),
            "discount_percent": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 0,
                    "max": 100,
                }
            ),
            "max_limit_usage": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 1,
                }
            ),
        }

    def clean_code(self):
        code = self.cleaned_data["code"]

        return code.strip().upper()