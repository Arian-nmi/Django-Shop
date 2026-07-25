from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from order.permissions import HasCustomerAccessPermission
from order.models import CouponModel
from cart.models import CartModel
from django.http import JsonResponse
from django.utils import timezone
from decimal import Decimal, ROUND_HALF_UP


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

