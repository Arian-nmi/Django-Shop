from django.urls import include, path
from . import views


app_name = "dashboard"

urlpatterns = [
    path("", views.DashboardHomeView.as_view(), name="home"),
    path("customer/", include("dashboard.customer.urls")),
    path("admin/", include("dashboard.admin.urls")),
]