from django.urls import path
from . import views


app_name = "review"

urlpatterns = [
    path("products/<str:slug>/submit/", views.SubmitReviewView.as_view(), name="submit"),
]