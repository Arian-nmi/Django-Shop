from django.urls import path
from . import views


app_name = "order"

urlpatterns = [
    path("validate-coupon/", views.ValidateCouponView.as_view(), name="validate-coupon"),
]