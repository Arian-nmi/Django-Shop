from rest_framework import serializers
from shop.models import ProductCategoryModel, ProductImageModel, ProductModel, WishlistProductModel


class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategoryModel

        fields = [
            "id",
            "title",
            "slug",
        ]


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImageModel

        fields = [
            "id",
            "file",
        ]


class ProductListSerializer(serializers.ModelSerializer):
    categories = ProductCategorySerializer(source="category", many=True, read_only=True)
    final_price = serializers.SerializerMethodField()
    is_discounted = serializers.SerializerMethodField()

    class Meta:
        model = ProductModel

        fields = [
            "id",
            "title",
            "slug",
            "image",
            "price",
            "discount_percent",
            "final_price",
            "is_discounted",
            "stock",
            "avg_rate",
            "categories",
        ]

    def get_final_price(self, obj):
        return obj.get_price()

    def get_is_discounted(self, obj):
        return obj.is_discounted()


class ProductDetailSerializer(ProductListSerializer):
    extra_images = ProductImageSerializer(source="product_images", many=True, read_only=True)

    class Meta(ProductListSerializer.Meta):
        fields = ProductListSerializer.Meta.fields + [
            "description",
            "brief_description",
            "extra_images",
            "created_date",
        ]


class WishlistProductSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)

    class Meta:
        model = WishlistProductModel

        fields = [
            "id",
            "product",
        ]


class AddWishlistProductSerializer(serializers.Serializer):
    product_id = serializers.IntegerField(min_value=1)