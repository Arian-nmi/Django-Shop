from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail

from .models import OrderModel, OrderStatusType


@shared_task(autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 3})
def send_order_confirmation_email(order_id):
    order = (
        OrderModel.objects
        .select_related("user", "payment")
        .prefetch_related("order_items__product")
        .get(pk=order_id)
    )

    if order.status != OrderStatusType.success.value:
        return {
            "sent": False,
            "reason": "Order is not successful.",
        }

    order_items_text = "\n".join(
        [
            (
                f"- {item.product.title} | "
                f"تعداد: {item.quantity} | "
                f"قیمت: {item.get_total_price()} تومان"
            )
            for item in order.order_items.all()
        ]
    )

    payment_ref_id = (
        order.payment.ref_id
        if order.payment and order.payment.ref_id
        else "-"
    )

    message = f"""
سلام،

پرداخت سفارش شماره {order.id} با موفقیت انجام شد.

محصولات سفارش:
{order_items_text}

مبلغ نهایی: {order.total_price} تومان
کد رهگیری پرداخت: {payment_ref_id}

آدرس ارسال:
{order.state}، {order.city}، {order.address}
کد پستی: {order.zip_code}

با تشکر
Django Shop
""".strip()

    send_mail(
        subject=f"تأیید سفارش شماره {order.id}",
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[order.user.email],
        fail_silently=False,
    )

    return {
        "sent": True,
        "order_id": order.id,
        "recipient": order.user.email,
    }