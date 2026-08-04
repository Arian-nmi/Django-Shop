from django.contrib import admin
from .models import ReviewModel


class ReviewModelAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "product",
        "rate",
        "status",
        "created_date",
    )

    list_filter = (
        "status",
        "rate",
        "created_date",
    )

    search_fields = (
        "user__email",
        "product__title",
        "description",
    )

    readonly_fields = (
        "user",
        "product",
        "created_date",
        "updated_date",
    )

admin.site.register(ReviewModel, ReviewModelAdmin)