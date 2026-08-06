from rest_framework import serializers
from order.models import OrderItemModel, OrderModel


class OrderProductSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    slug = serializers.CharField()
    image = serializers.ImageField()


class OrderItemSerializer(serializers.ModelSerializer):
    product = OrderProductSerializer(read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = OrderItemModel

        fields = [
            "id",
            "product",
            "quantity",
            "price",
            "total_price",
        ]

    def get_total_price(self, obj):
        return obj.get_total_price()


class OrderListSerializer(serializers.ModelSerializer):
    status_label = serializers.SerializerMethodField()
    payment_ref_id = serializers.SerializerMethodField()

    class Meta:
        model = OrderModel

        fields = [
            "id",
            "total_price",
            "status",
            "status_label",
            "payment_ref_id",
            "created_date",
        ]

    def get_status_label(self, obj):
        return obj.get_status()["label"]

    def get_payment_ref_id(self, obj):
        if obj.payment and obj.payment.ref_id:
            return obj.payment.ref_id

        return None


class OrderDetailSerializer(OrderListSerializer):
    items = OrderItemSerializer(source="order_items", many=True, read_only=True)
    coupon_code = serializers.SerializerMethodField()
    address_data = serializers.SerializerMethodField()

    class Meta(OrderListSerializer.Meta):
        fields = OrderListSerializer.Meta.fields + [
            "coupon_code",
            "address_data",
            "items",
            "updated_date",
        ]

    def get_coupon_code(self, obj):
        if obj.coupon:
            return obj.coupon.code

        return None

    def get_address_data(self, obj):
        return {
            "address": obj.address,
            "state": obj.state,
            "city": obj.city,
            "zip_code": obj.zip_code,
        }