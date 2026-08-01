from django.urls import include, path
from . import views


app_name = "admin"

urlpatterns = [
    path("", views.AdminDashboardHomeView.as_view(), name="home"),
    path("customer/", include("dashboard.customer.urls")),
]