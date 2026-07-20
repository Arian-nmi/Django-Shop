from django.db import models


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
        return sum(item.product.get_price() * item.quantity for item in self.cart_items.all())
    

class CartItemModel(models.Model):
    """
    Model representing an item in the shopping cart.
    """
    cart = models.ForeignKey(CartModel, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey('shop.ProductModel', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.product.title} - {self.cart.id}"