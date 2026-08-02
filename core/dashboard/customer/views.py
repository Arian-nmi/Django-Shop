from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.views.generic import (
    CreateView,
    DeleteView,
    ListView,
    TemplateView,
    UpdateView,
    DetailView,
)

from order.models import UserAddressModel, OrderModel, OrderStatusType
from shop.models import WishlistProductModel
from dashboard.permissions import CustomerDashboardRequiredMixin
from .forms import UserAddressForm


class CustomerDashboardHomeView(
    LoginRequiredMixin,
    CustomerDashboardRequiredMixin,
    TemplateView,
):
    template_name = "dashboard/customer/home.html"


class CustomerAddressListView(
    LoginRequiredMixin,
    CustomerDashboardRequiredMixin,
    ListView,
):
    template_name = (
        "dashboard/customer/addresses/address-list.html"
    )
    context_object_name = "addresses"

    def get_queryset(self):
        return UserAddressModel.objects.filter(
            user=self.request.user
        ).order_by("-created_date")


class CustomerAddressCreateView(
    LoginRequiredMixin,
    CustomerDashboardRequiredMixin,
    SuccessMessageMixin,
    CreateView,
):
    template_name = (
        "dashboard/customer/addresses/address-create.html"
    )
    form_class = UserAddressForm
    success_message = "آدرس جدید با موفقیت ثبت شد."

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            "dashboard:customer:address-list"
        )


class CustomerAddressUpdateView(
    LoginRequiredMixin,
    CustomerDashboardRequiredMixin,
    SuccessMessageMixin,
    UpdateView,
):
    template_name = (
        "dashboard/customer/addresses/address-edit.html"
    )
    form_class = UserAddressForm
    success_message = "آدرس با موفقیت ویرایش شد."

    def get_queryset(self):
        return UserAddressModel.objects.filter(
            user=self.request.user
        )

    def get_success_url(self):
        return reverse_lazy(
            "dashboard:customer:address-list"
        )


class CustomerAddressDeleteView(
    LoginRequiredMixin,
    CustomerDashboardRequiredMixin,
    SuccessMessageMixin,
    DeleteView,
):
    template_name = (
        "dashboard/customer/addresses/address-delete.html"
    )
    success_message = "آدرس با موفقیت حذف شد."

    def get_queryset(self):
        # جلوگیری از delete آدرس user دیگر
        return UserAddressModel.objects.filter(
            user=self.request.user
        )

    def get_success_url(self):
        return reverse_lazy(
            "dashboard:customer:address-list"
        )


class CustomerOrderListView(
    LoginRequiredMixin,
    CustomerDashboardRequiredMixin,
    ListView,
):
    template_name = (
        "dashboard/customer/orders/order-list.html"
    )
    context_object_name = "orders"
    paginate_by = 10

    ALLOWED_ORDERINGS = {
        "newest": "-created_date",
        "oldest": "created_date",
        "price_asc": "total_price",
        "price_desc": "-total_price",
    }

    def get_queryset(self):
        queryset = (
            OrderModel.objects
            .filter(user=self.request.user)
            .select_related("coupon", "payment")
            .prefetch_related("order_items__product")
        )

        search_query = self.request.GET.get("q", "").strip()

        if search_query.isdigit():
            queryset = queryset.filter(id=int(search_query))

        status = self.request.GET.get("status")

        valid_statuses = {
            str(status_id)
            for status_id, _ in OrderStatusType.choices
        }

        if status in valid_statuses:
            queryset = queryset.filter(status=int(status))

        order_by = self.request.GET.get("order_by")

        if order_by in self.ALLOWED_ORDERINGS:
            queryset = queryset.order_by(
                self.ALLOWED_ORDERINGS[order_by]
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["status_types"] = OrderStatusType.choices
        context["total_items"] = context["paginator"].count

        return context


class CustomerOrderDetailView(
    LoginRequiredMixin,
    CustomerDashboardRequiredMixin,
    DetailView,
):
    template_name = (
        "dashboard/customer/orders/order-detail.html"
    )
    context_object_name = "order"

    def get_queryset(self):
        return (
            OrderModel.objects
            .filter(user=self.request.user)
            .select_related("coupon", "payment")
            .prefetch_related("order_items__product")
        )


class CustomerOrderInvoiceView(
    LoginRequiredMixin,
    CustomerDashboardRequiredMixin,
    DetailView,
):
    template_name = (
        "dashboard/customer/orders/order-invoice.html"
    )
    context_object_name = "order"

    def get_queryset(self):
        return (
            OrderModel.objects.filter(
                    user=self.request.user,
                    status=OrderStatusType.success.value,
                )
            .select_related("coupon", "payment")
            .prefetch_related("order_items__product")
        )


class CustomerWishlistListView(
    LoginRequiredMixin,
    CustomerDashboardRequiredMixin,
    ListView,
):
    template_name = "dashboard/customer/wishlists/wishlist-list.html"
    context_object_name = "wishlist_items"
    paginate_by = 12

    ALLOWED_ORDERINGS = {
        "newest": "-id",
        "oldest": "id",
        "price_asc": "product__price",
        "price_desc": "-product__price",
    }

    def get_queryset(self):
        queryset = (
            WishlistProductModel.objects
            .filter(user=self.request.user)
            .select_related("product")
        )

        search_query = self.request.GET.get(
            "q",
            "",
        ).strip()

        if search_query:
            queryset = queryset.filter(
                product__title__icontains=search_query
            )

        order_by = self.request.GET.get("order_by")

        if order_by in self.ALLOWED_ORDERINGS:
            queryset = queryset.order_by(
                self.ALLOWED_ORDERINGS[order_by]
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["total_items"] = context["paginator"].count

        return context


class CustomerWishlistDeleteView(
    LoginRequiredMixin,
    CustomerDashboardRequiredMixin,
    View,
):
    http_method_names = ["post"]

    def post(self, request, *args, **kwargs):
        wishlist_item = get_object_or_404(
            WishlistProductModel,
            pk=kwargs["pk"],
            user=request.user,
        )

        wishlist_item.delete()

        messages.success(
            request,
            "محصول از لیست علاقه‌مندی‌ها حذف شد.",
        )

        return redirect(
            "dashboard:customer:wishlist-list"
        )