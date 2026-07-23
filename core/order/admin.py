from django.contrib import admin
from .models import (
    CouponModel,
    OrderItemModel,
    OrderModel,
    UserAddressModel,
)


@admin.register(UserAddressModel)
class UserAddressModelAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "state",
        "city",
        "zip_code",
        "created_date",
    )
    search_fields = (
        "user__email",
        "state",
        "city",
        "zip_code",
    )


@admin.register(CouponModel)
class CouponModelAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "code",
        "discount_percent",
        "max_limit_usage",
        "expiration_date",
    )
    search_fields = ("code",)
    filter_horizontal = ("used_by",)


class OrderItemInline(admin.TabularInline):
    model = OrderItemModel
    extra = 0
    readonly_fields = (
        "product",
        "quantity",
        "price",
    )


@admin.register(OrderModel)
class OrderModelAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "total_price",
        "status",
        "created_date",
    )
    list_filter = ("status",)
    search_fields = ("user__email",)
    inlines = (OrderItemInline,)