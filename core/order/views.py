from decimal import Decimal, ROUND_HALF_UP

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.http import JsonResponse
from django.utils import timezone
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import FormView, View, TemplateView

from cart.models import CartModel
from payment.models import PaymentModel
from payment.zarinpal_client import ZarinPalSandbox

from .forms import CheckOutForm
from .models import (
    CouponModel,
    OrderItemModel,
    OrderModel,
    OrderStatusType,
)
from .permissions import HasCustomerAccessPermission


class OrderCheckOutView(
    LoginRequiredMixin,
    HasCustomerAccessPermission,
    FormView,
):
    form_class = CheckOutForm
    template_name = "order/checkout.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        cart, _ = CartModel.objects.get_or_create(
            user=self.request.user
        )

        context["addresses"] = self.request.user.addresses.all()
        context["cart_items"] = cart.items.select_related("product")
        context["total_price"] = cart.calculate_total_price()

        return context

    def form_valid(self, form):
        user = self.request.user
        address = form.cleaned_data["address_id"]
        coupon = form.cleaned_data["coupon"]

        cart, _ = CartModel.objects.get_or_create(user=user)

        cart_items = list(
            cart.items.select_related("product")
        )

        if not cart_items:
            form.add_error(
                None,
                "سبد خرید شما خالی است.",
            )
            return self.form_invalid(form)

        try:
            with transaction.atomic():
                order = self.create_order(
                    user=user,
                    address=address,
                    coupon=coupon,
                )

                self.create_order_items(
                    order=order,
                    cart_items=cart_items,
                )

                self.set_final_order_price(
                    order=order,
                    coupon=coupon,
                )

            payment_url = self.create_payment_url(order)

        except ValueError as error:
            messages.error(
                self.request,
                str(error),
            )
            return self.form_invalid(form)

        except Exception:
            messages.error(
                self.request,
                "مشکلی در ساخت درخواست پرداخت به وجود آمد. "
                "لطفاً دوباره تلاش کنید.",
            )
            return self.form_invalid(form)

        return redirect(payment_url)

    def create_order(self, user, address, coupon):
        return OrderModel.objects.create(
            user=user,
            coupon=coupon,
            address=address.address,
            state=address.state,
            city=address.city,
            zip_code=address.zip_code,
            status=OrderStatusType.pending.value,
        )

    def create_order_items(self, order, cart_items):
        order_items = []

        for cart_item in cart_items:
            product = cart_item.product

            if not product.is_published():
                raise ValueError(
                    f"محصول «{product.title}» دیگر قابل خرید نیست."
                )

            if cart_item.quantity > product.stock:
                raise ValueError(
                    f"موجودی محصول «{product.title}» کافی نیست."
                )

            order_items.append(
                OrderItemModel(
                    order=order,
                    product=product,
                    quantity=cart_item.quantity,
                    price=product.get_price(),
                )
            )

        OrderItemModel.objects.bulk_create(order_items)

    def set_final_order_price(self, order, coupon):
        subtotal = order.calculate_total_price()
        discount_amount = Decimal("0")

        if coupon:
            discount_amount = (
                subtotal
                * Decimal(coupon.discount_percent)
                / Decimal("100")
            )

        final_price = (
            subtotal - discount_amount
        ).quantize(
            Decimal("1"),
            rounding=ROUND_HALF_UP,
        )

        order.total_price = final_price
        order.save(
            update_fields=[
                "total_price",
                "updated_date",
            ]
        )

    def create_payment_url(self, order):
        zarinpal = ZarinPalSandbox()

        callback_url = self.request.build_absolute_uri(
            reverse("payment:verify")
        )

        response = zarinpal.payment_request(
            amount_toman=order.total_price,
            description=f"پرداخت سفارش شماره {order.id}",
            callback_url=callback_url,
        )

        data = response.get("data", {})
        response_code = data.get("code")

        if response_code != 100:
            order.status = OrderStatusType.failed.value
            order.save(
                update_fields=[
                    "status",
                    "updated_date",
                ]
            )

            raise ValueError(
                "درخواست پرداخت توسط زرین‌پال پذیرفته نشد."
            )

        authority = data["authority"]

        payment = PaymentModel.objects.create(
            authority_id=authority,
            amount=order.total_price,
            response_code=response_code,
            response_json=response,
        )

        order.payment = payment
        order.save(
            update_fields=[
                "payment",
                "updated_date",
            ]
        )

        return zarinpal.generate_payment_url(authority)


class ValidateCouponView(LoginRequiredMixin, HasCustomerAccessPermission, View):

    def post(self, request, *args, **kwargs):
        code = request.POST.get("code")
        user = self.request.user
        status_code = 200
        message = "کد تخفیف با موفقیت ثبت شد"
        total_price = 0
        total_tax = 0

        try:
            coupon = CouponModel.objects.get(code=code)
        except CouponModel.DoesNotExist:
            return JsonResponse({"message": "کد تخفیف یافت نشد"}, status=404)
        else:
            if coupon.used_by.count() >= coupon.max_limit_usage:
                status_code, message = 403, "محدودیت در تعداد استفاده"

            elif coupon.expiration_date and coupon.expiration_date < timezone.now():
                status_code, message = 403, "کد تخفیف منقضی شده است"

            elif user in coupon.used_by.all():
                status_code, message = 403, "این کد تخفیف قبلا توسط شما استفاده شده است"

            else:
                cart, _ = CartModel.objects.get_or_create(user=self.request.user)
                if not cart.items.exists():
                    return JsonResponse(
                        {
                            "message": "سبد خرید شما خالی است.",
                        },
                        status=400,
                    )

                total_price = cart.calculate_total_price()
                discount_amount = (
                    total_price * Decimal(coupon.discount_percent) / Decimal("100")
                )

                total_price = (
                    total_price - discount_amount).quantize(Decimal("1"), rounding=ROUND_HALF_UP
                )
                total_tax = round((total_price * 9)/100)
        return JsonResponse(
                {
                    "message": message, 
                    "total_tax": int(total_tax), 
                    "total_price": int(total_price)
                },
                status=status_code
              )


class OrderCompletedView(TemplateView):
    template_name = "order/compeleted.html"


class OrderFailedView(TemplateView):
    template_name = "order/failed.html"