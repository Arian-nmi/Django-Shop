from django.db import models
from django.core.validators import MinValueValidator


class CartModel(models.Model):
    """
    Model representing a shopping cart.
    """
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart for {self.user.email}"
    
    def calculate_total_price(self):
        return sum(
            item.product.get_price() * item.quantity
            for item in self.items.select_related("product")
        )
    

class CartItemModel(models.Model):
    """
    Model representing an item in the shopping cart.
    """
    cart = models.ForeignKey(CartModel, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey('shop.ProductModel', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["cart", "product"],
                name="unique_cart_product",
            )
        ]

    def __str__(self):
        return f"{self.product.title} - {self.cart.id}"