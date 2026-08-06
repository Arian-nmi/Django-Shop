from rest_framework import serializers
from cart.models import CartItemModel, CartModel


class CartProductSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    slug = serializers.CharField()
    image = serializers.ImageField()
    price = serializers.DecimalField(max_digits=10, decimal_places=0)
    final_price = serializers.SerializerMethodField()

    def get_final_price(self, product):
        return product.get_price()


class CartItemSerializer(serializers.ModelSerializer):
    product = CartProductSerializer(read_only=True)
    unit_price = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = CartItemModel

        fields = [
            "id",
            "product",
            "quantity",
            "unit_price",
            "total_price",
        ]

    def get_unit_price(self, obj):
        return obj.product.get_price()

    def get_total_price(self, obj):
        return obj.product.get_price() * obj.quantity


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_quantity = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = CartModel

        fields = [
            "id",
            "items",
            "total_quantity",
            "total_price",
            "updated_date",
        ]

    def get_total_quantity(self, obj):
        return sum(item.quantity for item in obj.items.all())

    def get_total_price(self, obj):
        return sum((item.product.get_price() * item.quantity for item in obj.items.all()), 0)


class AddCartItemSerializer(serializers.Serializer):
    product_id = serializers.IntegerField(min_value=1)
    quantity = serializers.IntegerField(min_value=1, default=1)


class UpdateCartItemSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(min_value=1)