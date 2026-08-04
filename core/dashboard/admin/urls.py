from django.urls import include, path
from . import views


app_name = "admin"

urlpatterns = [
    path("", views.AdminDashboardHomeView.as_view(), name="home"),
    
    path("customer/", include("dashboard.customer.urls")),

    path("products/", views.AdminProductListView.as_view(), name="product-list"),
    path("products/create/", views.AdminProductCreateView.as_view(), name="product-create"),
    path("products/<int:pk>/edit/", views.AdminProductUpdateView.as_view(), name="product-edit"),
    path("products/<int:pk>/delete/", views.AdminProductDeleteView.as_view(), name="product-delete"),
    path("products/<int:pk>/images/add/", views.AdminProductAddImageView.as_view(), name="product-add-image"),
    path("products/<int:pk>/images/<int:image_id>/delete/", views.AdminProductRemoveImageView.as_view(), name="product-remove-image"),

    path("orders/", views.AdminOrderListView.as_view(), name="order-list"),
    path("orders/<int:pk>/detail/", views.AdminOrderDetailView.as_view(), name="order-detail"),
    path("orders/<int:pk>/invoice/", views.AdminOrderInvoiceView.as_view(), name="order-invoice"),
]