from django.core.cache import cache
from django.db import transaction
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import ProductCategoryModel, ProductImageModel, ProductModel


def clear_shop_api_cache():
    transaction.on_commit(cache.clear)


@receiver(post_save, sender=ProductModel)
@receiver(post_delete, sender=ProductModel)
@receiver(post_save, sender=ProductCategoryModel)
@receiver(post_delete, sender=ProductCategoryModel)
@receiver(post_save, sender=ProductImageModel)
@receiver(post_delete, sender=ProductImageModel)
def invalidate_shop_api_cache(sender, instance, **kwargs):
    clear_shop_api_cache()