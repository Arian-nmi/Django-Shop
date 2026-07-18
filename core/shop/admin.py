from django.contrib import admin
from .models import ProductModel, ProductImageModel, ProductCategoryModel, WishlistProductModel


class ProductModelAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "stock", "status", "price", "discount_percent", "created_date")


class ProductCategoryModelAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "created_date")


class ProductImageModelAdmin(admin.ModelAdmin):
    list_display = ("id", "file", "created_date")


class WishlistProductModelAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "product")


admin.site.register(ProductModel, ProductModelAdmin)
admin.site.register(ProductCategoryModel, ProductCategoryModelAdmin)
admin.site.register(ProductImageModel, ProductImageModelAdmin)
admin.site.register(WishlistProductModel, WishlistProductModelAdmin)