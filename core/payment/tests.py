from decimal import Decimal
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from order.models import OrderItemModel, OrderModel, OrderStatusType
from payment.models import PaymentModel, PaymentStatusType
from shop.models import ProductModel, ProductStatusType


class PaymentVerificationIdempotencyTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="payment-test@example.com",
            password="StrongPassword123!",
            is_verified=True,
        )

        self.product = ProductModel.objects.create(
            user=self.user,
            title="Test Product",
            slug="payment-idempotency-test-product",
            description="Test product",
            stock=10,
            status=ProductStatusType.publish.value,
            price=Decimal("100000"),
            discount_percent=0,
        )

        self.payment = PaymentModel.objects.create(
            authority_id="test-authority-123",
            amount=Decimal("200000"),
        )

        self.order = OrderModel.objects.create(
            user=self.user,
            payment=self.payment,
            address="Test address",
            state="Tehran",
            city="Tehran",
            zip_code="1234567890",
            total_price=Decimal("200000"),
            status=OrderStatusType.pending.value,
        )

        OrderItemModel.objects.create(
            order=self.order,
            product=self.product,
            quantity=2,
            price=Decimal("100000"),
        )

        self.verify_url = reverse("payment:verify")

    @patch("payment.views.send_order_confirmation_email.delay")
    @patch("payment.views.ZarinPalSandbox.payment_verify")
    def test_duplicate_successful_callback_decrements_stock_once(
        self,
        mock_payment_verify,
        mock_send_confirmation_email,
    ):
        mock_payment_verify.side_effect = [
            {
                "data": {
                    "code": 100,
                    "ref_id": 987654,
                }
            },
            {
                "data": {
                    "code": 101,
                    "ref_id": 987654,
                }
            },
        ]

        callback_data = {
            "Authority": self.payment.authority_id,
            "Status": "OK",
        }

        first_response = self.client.get(self.verify_url, callback_data)
        self.assertEqual(first_response.status_code, 302)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 8)

        second_response = self.client.get(self.verify_url, callback_data)

        self.assertEqual(second_response.status_code, 302)
        self.product.refresh_from_db()
        self.order.refresh_from_db()
        self.payment.refresh_from_db()

        self.assertEqual(self.product.stock, 8)
        self.assertEqual(self.order.status, OrderStatusType.success.value)
        self.assertEqual(self.payment.status,PaymentStatusType.success.value)