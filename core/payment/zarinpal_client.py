import requests
from django.conf import settings


class ZarinPalSandbox:
    payment_request_url = (
        "https://sandbox.zarinpal.com/pg/v4/payment/request.json"
    )

    payment_verify_url = (
        "https://sandbox.zarinpal.com/pg/v4/payment/verify.json"
    )

    payment_page_url = (
        "https://sandbox.zarinpal.com/pg/StartPay/"
    )

    def __init__(self, merchant_id=None):
        self.merchant_id = merchant_id or settings.ZARINPAL_MERCHANT_ID

    def payment_request(
        self,
        amount_toman,
        description="پرداخت سفارش",
        callback_url=None,
    ):
        payload = {
            "merchant_id": self.merchant_id,
            "amount": int(amount_toman) * 10,
            "callback_url": callback_url,
            "description": description,
        }

        response = requests.post(
            self.payment_request_url,
            json=payload,
            timeout=15,
        )

        response.raise_for_status()

        return response.json()

    def payment_verify(self, amount_toman, authority):
        payload = {
            "merchant_id": self.merchant_id,
            "amount": int(amount_toman) * 10,
            "authority": authority,
        }

        response = requests.post(
            self.payment_verify_url,
            json=payload,
            timeout=15,
        )

        response.raise_for_status()

        return response.json()

    def generate_payment_url(self, authority):
        return f"{self.payment_page_url}{authority}"