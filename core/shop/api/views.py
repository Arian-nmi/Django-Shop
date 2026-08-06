from decimal import Decimal, InvalidOperation
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from shop.models import ProductCategoryModel, ProductModel, ProductStatusType, WishlistProductModel
from .serializers import (
    ProductCategorySerializer, ProductDetailSerializer, ProductListSerializer, 
    WishlistProductSerializer, AddWishlistProductSerializer
    )

@method_decorator(cache_page(60 * 5), name="dispatch",)
class CategoryListAPIView(ListAPIView):
    serializer_class = ProductCategorySerializer
    permission_classes = [AllowAny]
    queryset = ProductCategoryModel.objects.all()


@method_decorator(cache_page(60 * 5), name="dispatch",)
class ProductListAPIView(ListAPIView):
    serializer_class = ProductListSerializer
    permission_classes = [AllowAny]

    ALLOWED_ORDERINGS = {
        "newest": "-created_date",
        "oldest": "created_date",
        "price_asc": "price",
        "price_desc": "-price",
        "title_asc": "title",
        "title_desc": "-title",
    }

    def get_queryset(self):
        queryset = ProductModel.objects.filter(status=ProductStatusType.publish.value).prefetch_related("category")
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


@method_decorator(cache_page(60 * 5), name="dispatch",)
class ProductDetailAPIView(RetrieveAPIView):
    serializer_class = ProductDetailSerializer
    permission_classes = [AllowAny]
    lookup_field = "slug"
    queryset = ProductModel.objects.filter(status=ProductStatusType.publish.value).prefetch_related("category", "product_images")


class WishlistAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        wishlist_items = (
            WishlistProductModel.objects
            .filter(user=request.user)
            .select_related("product")
            .prefetch_related("product__category")
        )

        return Response(WishlistProductSerializer(wishlist_items, many=True).data)

    def post(self, request):
        serializer = AddWishlistProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        product_id = serializer.validated_data["product_id"]
        product = get_object_or_404(ProductModel, pk=product_id, status=ProductStatusType.publish.value)
        wishlist_item, created = WishlistProductModel.objects.get_or_create(user=request.user, product=product)
        response_status = status.HTTP_201_CREATED if created else status.HTTP_200_OK

        return Response(WishlistProductSerializer(wishlist_item).data, status=response_status)


class WishlistItemDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, product_id):
        wishlist_item = get_object_or_404(WishlistProductModel, user=request.user, product_id=product_id)
        wishlist_item.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)