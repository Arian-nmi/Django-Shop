from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views import View

from order.models import OrderItemModel, OrderStatusType
from shop.models import ProductModel, ProductStatusType

from .forms import SubmitReviewForm
from .models import ReviewModel


class SubmitReviewView(LoginRequiredMixin, View):
    http_method_names = ["post"]

    def post(self, request, slug, *args, **kwargs):
        product = get_object_or_404(
            ProductModel,
            slug=slug,
            status=ProductStatusType.publish.value,
        )

        has_purchased_product = (
            OrderItemModel.objects
            .filter(
                order__user=request.user,
                order__status=OrderStatusType.success.value,
                product=product,
            )
            .exists()
        )

        if not has_purchased_product:
            messages.error(request, "فقط خریداران این محصول می‌توانند نظر ثبت کنند.")

            return redirect("shop:product-detail", slug=product.slug)

        if ReviewModel.objects.filter(user=request.user, product=product).exists():
            messages.error(request, "شما قبلاً برای این محصول نظر ثبت کرده‌اید.")

            return redirect("shop:product-detail", slug=product.slug)

        form = SubmitReviewForm(request.POST)

        if not form.is_valid():
            messages.error(request, "اطلاعات نظر معتبر نیست.")

            return redirect("shop:product-detail", slug=product.slug)

        review = form.save(commit=False)
        review.user = request.user
        review.product = product
        review.save()

        messages.success(request, "نظر شما ثبت شد و پس از بررسی نمایش داده می‌شود.")

        return redirect("shop:product-detail", slug=product.slug)
