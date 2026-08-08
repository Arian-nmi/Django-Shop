from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import View

from accounts.models import UserType


class DashboardHomeView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        if request.user.is_staff or request.user.is_superuser:
            return redirect(reverse_lazy("dashboard:admin:home"))

        if request.user.type == UserType.customer.value:
            return redirect(reverse_lazy("dashboard:customer:home"))

        return redirect(reverse_lazy("website:index"))