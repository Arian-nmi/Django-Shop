from django.contrib import admin
from .models import PaymentModel


class PaymentModelAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "authority_id",
        "amount",
        "response_code",
        "status",
        "created_date"
    )
    
    list_filter = (
        "status",
        "created_date",
    )

    search_fields = (
        "authority_id",
        "ref_id",
    )

    readonly_fields = (
        "authority_id",
        "ref_id",
        "amount",
        "response_code",
        "response_json",
        "status",
        "created_date",
        "updated_date",
    )

    ordering = ("-created_date",)

admin.site.register(PaymentModel, PaymentModelAdmin)