from django.urls import path
from . import views


urlpatterns = [
    path("", views.CartAPIView.as_view(), name="cart"),
    path("items/", views.CartItemCreateAPIView.as_view(), name="cart-item-create"),
    path("items/<int:product_id>/", views.CartItemDetailAPIView.as_view(), name="cart-item-detail"),
]