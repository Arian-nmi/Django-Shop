from django.urls import path
from . import views


urlpatterns = [
    path("categories/", views.CategoryListAPIView.as_view(), name="category-list"),
    path("products/", views.ProductListAPIView.as_view(), name="product-list"),
    path("products/<str:slug>/", views.ProductDetailAPIView.as_view(), name="product-detail"),
    path("wishlist/", views.WishlistAPIView.as_view(), name="wishlist"),
    path("wishlist/<int:product_id>/", views.WishlistItemDetailAPIView.as_view(), name="wishlist-item-detail"),
]