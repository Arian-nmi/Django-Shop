from decimal import Decimal

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User
from order.models import OrderItemModel, OrderModel, OrderStatusType
from shop.models import ProductCategoryModel, ProductModel, ProductStatusType


class APIBaseTestCase(APITestCase):
    def setUp(self):
        self.password = "StrongPassword123!"

        self.customer = User.objects.create_user(
            email="customer@example.com",
            password=self.password,
            is_verified=True,
        )

        self.other_customer = User.objects.create_user(
            email="other@example.com",
            password=self.password,
            is_verified=True,
        )

        self.staff_user = User.objects.create_user(
            email="staff@example.com",
            password=self.password,
            is_staff=True,
            is_verified=True,
        )

        self.category = ProductCategoryModel.objects.create(
            title="پوشاک",
            slug="clothes",
        )

        self.published_product = ProductModel.objects.create(
            user=self.staff_user,
            title="تیشرت تست",
            slug="test-tshirt",
            description="توضیحات محصول تست",
            brief_description="توضیح کوتاه",
            stock=10,
            status=ProductStatusType.publish.value,
            price=Decimal("100000"),
            discount_percent=10,
        )

        self.published_product.category.add(self.category)

        self.draft_product = ProductModel.objects.create(
            user=self.staff_user,
            title="محصول Draft",
            slug="draft-product",
            description="این محصول نباید API عمومی نمایش داده شود.",
            stock=5,
            status=ProductStatusType.draft.value,
            price=Decimal("50000"),
        )

    def get_token(self, user):
        response = self.client.post(
            reverse("api:token-obtain-pair"),
            {
                "email": user.email,
                "password": self.password,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        return response.data["access"]

    def authenticate(self, user):
        access_token = self.get_token(user)

        self.client.credentials(HTTP_AUTHORIZATION=(f"Bearer {access_token}"))

    def create_successful_order(self, user, product):
        order = OrderModel.objects.create(
            user=user,
            address="خیابان آزادی، پلاک 10",
            state="تهران",
            city="تهران",
            zip_code="1234567890",
            total_price=product.get_price(),
            status=OrderStatusType.success.value,
        )

        OrderItemModel.objects.create(
            order=order,
            product=product,
            quantity=1,
            price=product.get_price(),
        )

        return order