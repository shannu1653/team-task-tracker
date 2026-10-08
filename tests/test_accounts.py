from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import User


class AccountAPITests(APITestCase):
    def test_register_user(self):
        response = self.client.post(
            "/auth/register/",
            {
                "name": "John Doe",
                "email": "john@example.com",
                "password": "Password@123",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )
        self.assertEqual(
            response.data["email"],
            "john@example.com",
        )
        self.assertNotIn(
            "password",
            response.data,
        )
        self.assertEqual(
            User.objects.count(),
            1,
        )

    def test_password_is_stored_as_a_hash(self):
        password = "Password@123"

        response = self.client.post(
            "/auth/register/",
            {
                "name": "John Doe",
                "email": "john@example.com",
                "password": password,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        user = User.objects.get(
            email="john@example.com"
        )

        self.assertNotEqual(
            user.password,
            password,
        )
        self.assertTrue(
            user.check_password(password)
        )

    def test_duplicate_email_is_rejected_case_insensitively(self):
        User.objects.create_user(
            email="john@example.com",
            name="John Doe",
            password="Password@123",
        )

        response = self.client.post(
            "/auth/register/",
            {
                "name": "Another User",
                "email": "JOHN@EXAMPLE.COM",
                "password": "Password@123",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_short_password_is_rejected(self):
        response = self.client.post(
            "/auth/register/",
            {
                "name": "John Doe",
                "email": "john@example.com",
                "password": "short",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_login_returns_jwt_tokens(self):
        User.objects.create_user(
            email="john@example.com",
            name="John Doe",
            password="Password@123",
        )

        response = self.client.post(
            "/auth/login/",
            {
                "email": "john@example.com",
                "password": "Password@123",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertIn(
            "access",
            response.data,
        )
        self.assertIn(
            "refresh",
            response.data,
        )
        self.assertIn(
            "user",
            response.data,
        )
        self.assertNotIn(
            "password",
            response.data["user"],
        )

    def test_invalid_login_is_rejected(self):
        User.objects.create_user(
            email="john@example.com",
            name="John Doe",
            password="Password@123",
        )

        response = self.client.post(
            "/auth/login/",
            {
                "email": "john@example.com",
                "password": "WrongPassword@123",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_logout_blacklists_refresh_token(self):
        User.objects.create_user(
            email="john@example.com",
            name="John Doe",
            password="Password@123",
        )

        login_response = self.client.post(
            "/auth/login/",
            {
                "email": "john@example.com",
                "password": "Password@123",
            },
            format="json",
        )

        self.assertEqual(
            login_response.status_code,
            status.HTTP_200_OK,
        )

        refresh_token = login_response.data["refresh"]
        access_token = login_response.data["access"]

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {access_token}"
        )

        logout_response = self.client.post(
            "/auth/logout/",
            {
                "refresh": refresh_token,
            },
            format="json",
        )

        self.assertEqual(
            logout_response.status_code,
            status.HTTP_205_RESET_CONTENT,
        )

        with self.assertRaises(TokenError):
            RefreshToken(refresh_token)