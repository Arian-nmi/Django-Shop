from django import template
from shop.models import ProductModel, ProductStatusType


register = template.Library()

@register.inclusion_tag("shop/includes/latest-products.html")
def show_latest_products(count=6):
    products = ProductModel.objects.filter(status=ProductStatusType.publish.value).order_by("-created_date")[:count]
    return {"products": products}


@register.inclusion_tag("shop/includes/similar-products.html")
def show_similar_products(product, count=4):
    products = ProductModel.objects.filter(
        status=ProductStatusType.publish.value,
        category__in=product.category.all()
    ).exclude(id=product.id).distinct()[:count]
    return {"products": products}