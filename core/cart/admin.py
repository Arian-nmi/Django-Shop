from django.contrib import admin
from .models import CartModel,CartItemModel


class CartModelAdmin(admin.ModelAdmin):
    list_display = ("id", "user")


class CartItemModelAdmin(admin.ModelAdmin):
    list_display = ("id", "cart","product","quantity")


admin.site.register(CartModel, CartModelAdmin)
admin.site.register(CartItemModel, CartItemModelAdmin)