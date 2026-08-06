from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from cart.models import CartItemModel, CartModel
from shop.models import ProductModel, ProductStatusType

from .serializers import AddCartItemSerializer, CartSerializer, UpdateCartItemSerializer


class CartMixin:
    def get_cart(self):
        cart, _ = CartModel.objects.get_or_create(user=self.request.user)

        return CartModel.objects.prefetch_related("items__product").get(pk=cart.pk)
        
    def get_published_product(self, product_id):
        return get_object_or_404(ProductModel, pk=product_id, status=ProductStatusType.publish.value)

    def get_cart_response(self, cart):
        cart = CartModel.objects.prefetch_related("items__product").get(pk=cart.pk)

        return Response(CartSerializer(cart).data)


class CartAPIView(CartMixin, APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart = self.get_cart()

        return self.get_cart_response(cart)


class CartItemCreateAPIView(CartMixin, APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AddCartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        product_id = serializer.validated_data["product_id"]
        quantity_to_add = serializer.validated_data["quantity"]

        product = self.get_published_product(product_id)
        cart = self.get_cart()
        cart_item, created = CartItemModel.objects.get_or_create(cart=cart, product=product, defaults={"quantity": 0})
        new_quantity = cart_item.quantity + quantity_to_add

        if new_quantity > product.stock:
            if created:
                cart_item.delete()

            return Response(
                {
                    "detail": (
                        "موجودی محصول برای تعداد "
                        "درخواستی کافی نیست."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        cart_item.quantity = new_quantity
        cart_item.save(update_fields=["quantity", "updated_date"])

        return self.get_cart_response(cart)


class CartItemDetailAPIView(CartMixin, APIView):
    permission_classes = [IsAuthenticated]

    def get_cart_item(self, product_id):
        cart = self.get_cart()
        cart_item = get_object_or_404(CartItemModel, cart=cart, product_id=product_id)

        return cart, cart_item

    def patch(self, request, product_id):
        serializer = UpdateCartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        cart, cart_item = self.get_cart_item( product_id)

        requested_quantity = serializer.validated_data["quantity"]

        if requested_quantity > cart_item.product.stock:
            return Response(
                {
                    "detail": (
                        "موجودی محصول برای تعداد "
                        "درخواستی کافی نیست."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        cart_item.quantity = requested_quantity
        cart_item.save(update_fields=["quantity", "updated_date"])

        return self.get_cart_response(cart)

    def delete(self, request, product_id):
        cart, cart_item = self.get_cart_item(product_id)
        cart_item.delete()

        return self.get_cart_response(cart)