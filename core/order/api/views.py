from rest_framework.generics import  ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated

from order.models import OrderModel
from .serializers import OrderDetailSerializer, OrderListSerializer


class OrderListAPIView(ListAPIView):
    serializer_class = OrderListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return OrderModel.objects.filter(user=self.request.user).select_related("payment", "coupon")


class OrderDetailAPIView(RetrieveAPIView):
    serializer_class = OrderDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            OrderModel.objects
            .filter(user=self.request.user)
            .select_related("payment", "coupon")
            .prefetch_related("order_items__product")
        )
        
