from django.db import transaction
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import View

from cart.models import CartModel
from order.models import OrderModel, OrderStatusType
from .models import PaymentModel, PaymentStatusType

from order.tasks import send_order_confirmation_email
from cart.cart import CartSession
from .zarinpal_client import ZarinPalSandbox


class PaymentVerifyView(View):
    def get(self, request, *args, **kwargs):
        authority_id = request.GET.get("Authority")
        callback_status = request.GET.get("Status")

        if not authority_id:
            return redirect(reverse_lazy("order:failed"))

        payment_obj = get_object_or_404(
            PaymentModel,
            authority_id=authority_id,
        )

        order = get_object_or_404(
            OrderModel,
            payment=payment_obj,
        )

        if callback_status != "OK":
            payment_obj.status = PaymentStatusType.failed.value
            payment_obj.response_json = {
                "callback_status": callback_status,
            }
            payment_obj.save(
                update_fields=[
                    "status",
                    "response_json",
                    "updated_date",
                ]
            )

            order.status = OrderStatusType.failed.value
            order.save(
                update_fields=[
                    "status",
                    "updated_date",
                ]
            )

            return redirect(reverse_lazy("order:failed"))

        zarinpal = ZarinPalSandbox()

        try:
            response = zarinpal.payment_verify(
                amount_toman=payment_obj.amount,
                authority=payment_obj.authority_id,
            )
        except Exception:
            return redirect(reverse_lazy("order:failed"))

        data = response.get("data", {})
        status_code = data.get("code")
        ref_id = data.get("ref_id")

        is_successful = status_code in {100, 101}

        with transaction.atomic():
            payment_obj.ref_id = ref_id
            payment_obj.response_code = status_code
            payment_obj.response_json = response

            payment_obj.status = (
                PaymentStatusType.success.value
                if is_successful
                else PaymentStatusType.failed.value
            )

            payment_obj.save(
                update_fields=[
                    "ref_id",
                    "response_code",
                    "response_json",
                    "status",
                    "updated_date",
                ]
            )

            order.status = (
                OrderStatusType.success.value
                if is_successful
                else OrderStatusType.failed.value
            )

            if is_successful:
                for order_item in order.order_items.select_related("product"):
                    product = order_item.product

                    product.stock -= order_item.quantity

                    product.save(update_fields=["stock", "updated_date"])

                if order.coupon:
                    order.coupon.used_by.add(order.user)

                cart = CartModel.objects.filter(user=order.user).first()

                if cart:
                    cart.items.all().delete()

            order.save(update_fields=["status", "updated_date"])

        if is_successful:
            CartSession(request.session).clear()
            transaction.on_commit(lambda: send_order_confirmation_email.delay(order.id))
            
        return redirect(
            reverse_lazy("order:completed")
            if is_successful
            else reverse_lazy("order:failed")
        )