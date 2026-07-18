from decimal import Decimal, InvalidOperation

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError, transaction
from django.http import JsonResponse
from django.views import View
from django.views.generic import DetailView, ListView

from .models import (
    ProductCategoryModel,
    ProductModel,
    ProductStatusType,
    WishlistProductModel,
)


class ShopProductGridView(ListView):
    template_name = "shop/product-grid.html"
    context_object_name = "products"
    paginate_by = 9

    ALLOWED_ORDERINGS = {
        "newest": "-created_date",
        "oldest": "created_date",
        "price_asc": "price",
        "price_desc": "-price",
        "title_asc": "title",
        "title_desc": "-title",
    }

    def get_paginate_by(self, queryset):
        try:
            page_size = int(self.request.GET.get("page_size", self.paginate_by))
        except (TypeError, ValueError):
            return self.paginate_by

        # جلوگیری از درخواست‌های خیلی سنگین
        return min(max(page_size, 1), 48)

    def get_queryset(self):
        queryset = (
            ProductModel.objects
            .filter(status=ProductStatusType.publish.value)
            .select_related("user")
            .prefetch_related("category")
        )

        search_query = self.request.GET.get("q", "").strip()
        if search_query:
            queryset = queryset.filter(title__icontains=search_query)

        category_id = self.request.GET.get("category_id")
        if category_id:
            try:
                queryset = queryset.filter(category__id=int(category_id))
            except (TypeError, ValueError):
                pass

        min_price = self.request.GET.get("min_price")
        if min_price:
            try:
                queryset = queryset.filter(price__gte=Decimal(min_price))
            except (InvalidOperation, TypeError, ValueError):
                pass

        max_price = self.request.GET.get("max_price")
        if max_price:
            try:
                queryset = queryset.filter(price__lte=Decimal(max_price))
            except (InvalidOperation, TypeError, ValueError):
                pass

        order_by = self.request.GET.get("order_by")
        if order_by in self.ALLOWED_ORDERINGS:
            queryset = queryset.order_by(self.ALLOWED_ORDERINGS[order_by])

        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["total_items"] = context["paginator"].count
        context["categories"] = ProductCategoryModel.objects.all()

        if self.request.user.is_authenticated:
            context["wishlist_items"] = set(
                WishlistProductModel.objects.filter(
                    user=self.request.user
                ).values_list("product_id", flat=True)
            )
        else:
            context["wishlist_items"] = set()

        return context


class ShopProductDetailView(DetailView):
    template_name = "shop/product-detail.html"
    context_object_name = "product"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    queryset = (
        ProductModel.objects
        .filter(status=ProductStatusType.publish.value)
        .select_related("user")
        .prefetch_related("category", "product_images")
    )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.object

        context["is_wished"] = False

        if self.request.user.is_authenticated:
            context["is_wished"] = WishlistProductModel.objects.filter(
                user=self.request.user,
                product=product,
            ).exists()

        return context


class AddOrRemoveWishlistView(LoginRequiredMixin, View):
    http_method_names = ["post"]

    def post(self, request, *args, **kwargs):
        product_id = request.POST.get("product_id")

        if not product_id:
            return JsonResponse(
                {
                    "message": "شناسه محصول ارسال نشده است.",
                    "is_wished": False,
                },
                status=400,
            )

        try:
            product = ProductModel.objects.get(
                id=product_id,
                status=ProductStatusType.publish.value,
            )
        except (ProductModel.DoesNotExist, ValueError):
            return JsonResponse(
                {
                    "message": "محصول موردنظر یافت نشد.",
                    "is_wished": False,
                },
                status=404,
            )

        wishlist_item = WishlistProductModel.objects.filter(
            user=request.user,
            product=product,
        ).first()

        if wishlist_item:
            wishlist_item.delete()

            return JsonResponse(
                {
                    "message": "محصول از لیست علاقه‌مندی‌ها حذف شد.",
                    "is_wished": False,
                    "product_id": product.id,
                }
            )

        try:
            with transaction.atomic():
                WishlistProductModel.objects.create(
                    user=request.user,
                    product=product,
                )
        except IntegrityError:
            return JsonResponse(
                {
                    "message": "محصول از قبل در لیست علاقه‌مندی‌ها وجود دارد.",
                    "is_wished": True,
                    "product_id": product.id,
                }
            )

        return JsonResponse(
            {
                "message": "محصول به لیست علاقه‌مندی‌ها اضافه شد.",
                "is_wished": True,
                "product_id": product.id,
            }
        )