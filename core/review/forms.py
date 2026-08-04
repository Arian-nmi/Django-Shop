from django import forms
from .models import ReviewModel


class SubmitReviewForm(forms.ModelForm):
    class Meta:
        model = ReviewModel

        fields = [
            "rate",
            "description",
        ]

        widgets = {
            "rate": forms.Select(
                choices=[
                    (1, "1 ستاره"),
                    (2, "2 ستاره"),
                    (3, "3 ستاره"),
                    (4, "4 ستاره"),
                    (5, "5 ستاره"),
                ],
                attrs={
                    "class": "form-select",
                },
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "نظر خود را درباره این محصول بنویسید...",
                },
            ),
        }