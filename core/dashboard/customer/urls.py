from django.urls import path
from . import views


app_name = "customer"

urlpatterns = [
    path("", views.CustomerDashboardHomeView.as_view(), name="home"),
    path("addresses/", views.CustomerAddressListView.as_view(), name="address-list"),
    path("addresses/create/", views.CustomerAddressCreateView.as_view(), name="address-create"),
    path("addresses/<int:pk>/edit/", views.CustomerAddressUpdateView.as_view(), name="address-edit"),
    path("addresses/<int:pk>/delete/", views.CustomerAddressDeleteView.as_view(), name="address-delete"),
    path("orders/", views.CustomerOrderListView.as_view(), name="order-list"),
    path("orders/<int:pk>/detail/", views.CustomerOrderDetailView.as_view(), name="order-detail"),
    path("orders/<int:pk>/invoice/", views.CustomerOrderInvoiceView.as_view(), name="order-invoice"),
]