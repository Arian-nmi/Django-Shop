from api.tests.base import APIBaseTestCase
from django.urls import reverse
from rest_framework import status


class JWTAuthenticationAPITest(APIBaseTestCase):
    def test_user_can_obtain_jwt_token(self):
        response = self.client.post(reverse("api:token-obtain-pair"),
            {
                "email": self.customer.email,
                "password": self.password,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_invalid_password_cannot_obtain_token(self):
        response = self.client.post(
            reverse("api:token-obtain-pair"),
            {
                "email": self.customer.email,
                "password": "wrong-password",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)