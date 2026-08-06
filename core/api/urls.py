from django.urls import include, path


app_name = "api"

urlpatterns = [
    path("auth/", include("api.auth_urls")),
    path("shop/", include("shop.api.urls")),
    path("cart/", include("cart.api.urls")),
    path("orders/", include("order.api.urls")),
]