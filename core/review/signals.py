from django.db.models import Avg
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import ReviewModel, ReviewStatusType


def update_product_average_rate(product):
    average_rate = (
        ReviewModel.objects
        .filter(product=product,status=ReviewStatusType.accepted.value)
        .aggregate(average=Avg("rate"))
        .get("average")
    )
    product.avg_rate = round(float(average_rate or 0), 1)
    product.save(update_fields=["avg_rate", "updated_date"])


@receiver(post_save, sender=ReviewModel)
def calculate_product_average_rate_on_save(sender, instance, **kwargs):
    update_product_average_rate(instance.product)


@receiver(post_delete, sender=ReviewModel)
def calculate_product_average_rate_on_delete(sender, instance, **kwargs):
    update_product_average_rate(instance.product)