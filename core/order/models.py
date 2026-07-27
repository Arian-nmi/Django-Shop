from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from decimal import Decimal


class OrderStatusType(models.IntegerChoices):
    pending = (1, "در انتظار پرداخت")
    success = (2, "موفقیت آمیز")
    failed = (3, "لغو شده")


class UserAddressModel(models.Model):
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name="addresses")

    address = models.CharField(max_length=250)
    state = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    zip_code = models.CharField(max_length=50)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)


class CouponModel(models.Model):
    used_by = models.ManyToManyField('accounts.User', related_name ="coupon_users", blank=True)

    code = models.CharField(max_length=100, unique=True)
    discount_percent = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    max_limit_usage = models.PositiveIntegerField(default=10, validators=[MinValueValidator(1)])
    expiration_date = models.DateTimeField(null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.code

class OrderModel(models.Model):
    user = models.ForeignKey('accounts.User', on_delete=models.PROTECT, related_name="orders")
    coupon = models.ForeignKey(CouponModel, on_delete=models.PROTECT, null=True, blank=True)
    payment = models.OneToOneField(
        "payment.PaymentModel",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="order",
    )

    address = models.CharField(max_length=250)
    state = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    zip_code = models.CharField(max_length=50)  
    total_price = models.DecimalField(default=0, max_digits=10, decimal_places=0)
    status = models.IntegerField(choices=OrderStatusType.choices, default=OrderStatusType.pending.value)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ["-created_date"]
    
    def calculate_total_price(self):
        return sum(
            (
                item.price * item.quantity
                for item in self.order_items.all()
            ),
            Decimal("0"),
        )
    
    def __str__(self):
        return f"{self.user.email} - {self.city}"
    
    def get_status(self):
        return {
            "id":self.status,
            "title":OrderStatusType(self.status).name,
            "label":OrderStatusType(self.status).label,
        }
        
    def get_full_address(self):
        return f"{self.state}, {self.city}, {self.address}"
    
    @property
    def is_successful(self):
        return self.status == OrderStatusType.success.value
    
    def get_price(self):
        if self.coupon:
            return round(self.total_price - (self.total_price * Decimal(self.coupon.discount_percent / 100)))
        return self.total_price


class OrderItemModel(models.Model):
    order = models.ForeignKey(OrderModel, on_delete=models.CASCADE, related_name="order_items") 
    product = models.ForeignKey('shop.ProductModel', on_delete=models.PROTECT)

    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    price = models.DecimalField(default=0, max_digits=10, decimal_places=0)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["order", "product"],
                name="unique_order_product",
            )
        ]
    
    def __str__(self):
        return f"{self.product.title} - {self.order.id}"

    def get_total_price(self):
        return self.price * self.quantity