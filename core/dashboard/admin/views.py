from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from dashboard.permissions import StaffDashboardRequiredMixin


class AdminDashboardHomeView(
    LoginRequiredMixin,
    StaffDashboardRequiredMixin,
    TemplateView,
):
    template_name = "dashboard/admin/home.html"