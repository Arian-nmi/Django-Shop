from django.db import models
from django.db.models import JSONField


class PaymentStatusType(models.IntegerChoices):
    pending = 1, "در انتظار"
    success = 2, "پرداخت موفق"
    failed = 3, "پرداخت ناموفق"


# Create your models here.
class PaymentModel(models.Model):
    authority_id = models.CharField(max_length=255, unique=True)
    ref_id = models.BigIntegerField(null=True, blank=True)
    amount = models.DecimalField(default=0, max_digits=10, decimal_places=0)
    response_json = JSONField(default=dict, blank=True)
    response_code = models.IntegerField(null=True, blank=True)
    status = models.IntegerField(choices=PaymentStatusType.choices, default=PaymentStatusType.pending.value)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ["-created_date"]
        indexes = [
            models.Index(fields=["authority_id"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"{self.authority_id}"
