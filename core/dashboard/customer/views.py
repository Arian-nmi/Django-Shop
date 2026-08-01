from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    ListView,
    TemplateView,
    UpdateView,
)

from order.models import UserAddressModel

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