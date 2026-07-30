from shop.models import ProductModel, ProductStatusType
from .models import CartModel, CartItemModel
from decimal import Decimal


class CartSession:
    def __init__(self, session):
        self.session = session
        self._cart = self.session.setdefault("cart", {"items": []})

        if "items" not in self._cart:
            self._cart["items"] = self._cart.pop("item", [])
            self.session.modified = True

    def update_product_quantity(self, product_id, quantity):
        try:
            quantity = int(quantity)
        except (TypeError, ValueError):
            return

        if quantity < 1:
            self.remove_product(product_id)
            return

        for item in self._cart["items"]:
            if item["product_id"] == str(product_id):
                item["quantity"] = quantity
                self.save()
                return

    def remove_product(self, product_id):
        for item in self._cart["items"]:
            if product_id == item["product_id"]:
                self._cart["items"].remove(item)
                break
        else:
            return
        self.save()

    def add_product(self, product_id):
        for item in self._cart["items"]:
            if product_id == item["product_id"]:
                item["quantity"] += 1
                break
        else:
            new_item = {"product_id": product_id, "quantity": 1}
            self._cart["items"].append(new_item)
        self.save()

    def clear(self):
        self._cart = self.session["cart"] = {"items": []}
        self.save()

    def get_cart_dict(self):
        return self._cart

    def get_cart_items(self):
        session_items = self._cart.get("items", [])

        product_ids = [
            item.get("product_id")
            for item in session_items
            if item.get("product_id")
        ]

        products = {
            str(product.id): product
            for product in ProductModel.objects.filter(
                id__in=product_ids,
                status=ProductStatusType.publish.value,
            )
        }

        cart_items = []
        valid_session_items = []

        for session_item in session_items:
            product_id = str(session_item.get("product_id", ""))
            product = products.get(product_id)

            try:
                quantity = int(session_item.get("quantity", 0))
            except (TypeError, ValueError):
                continue

            if not product or quantity < 1:
                continue

            valid_session_items.append(
                {
                    "product_id": product_id,
                    "quantity": quantity,
                }
            )

            cart_items.append(
                {
                    "product_id": product_id,
                    "quantity": quantity,
                    "product_obj": product,
                    "total_price": product.get_price() * quantity,
                }
            )

        if valid_session_items != session_items:
            self._cart["items"] = valid_session_items
            self.save()

        return cart_items


    def get_total_payment_amount(self):
        return sum(
            (
                item["total_price"]
                for item in self.get_cart_items()
            ),
            Decimal("0"),
        )


    def get_total_quantity(self):
        return sum(
            item.get("quantity", 0)
            for item in self._cart.get("items", [])
        )

    def save(self):
        self.session.modified = True

    def sync_cart_items_from_db(self,user):
        cart, created = CartModel.objects.get_or_create(user=user)
        cart_items = CartItemModel.objects.filter(cart=cart)

        for cart_item in cart_items:
            for item in self._cart["items"]:
                if str(cart_item.product.id) == item["product_id"]:
                    cart_item.quantity = item["quantity"]
                    cart_item.save()
                    break
            else:
                new_item = {"product_id": str(cart_item.product.id), "quantity": cart_item.quantity}
                self._cart["items"].append(new_item)
        self.merge_session_cart_in_db(user)
        self.save()

    def merge_session_cart_in_db(self,user):
        cart,created = CartModel.objects.get_or_create(user=user)

        for item in  self._cart["items"]:
            product_obj = ProductModel.objects.get(id=item["product_id"], status=ProductStatusType.publish.value)

            cart_item ,created = CartItemModel.objects.get_or_create(cart=cart,product=product_obj)
            cart_item.quantity = item["quantity"]
            cart_item.save()

        session_product_ids = [item["product_id"] for item in  self._cart["items"]]
        CartItemModel.objects.filter(cart=cart).exclude(product__id__in=session_product_ids).delete()