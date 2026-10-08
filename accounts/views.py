from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiResponse,
    extend_schema,
)
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import (
    LoginSerializer,
    LogoutSerializer,
    RegisterSerializer,
)


class RegisterView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=RegisterSerializer,
        responses={
            201: OpenApiResponse(
                description="User registered successfully.",
                examples=[
                    OpenApiExample(
                        "Registration Success",
                        value={
                            "id": 1,
                            "name": "John Doe",
                            "email": "john@example.com",
                        },
                        response_only=True,
                    ),
                ],
            ),
        },
        examples=[
            OpenApiExample(
                "Registration Request",
                value={
                    "name": "John Doe",
                    "email": "john@example.com",
                    "password": "Password@123",
                },
                request_only=True,
            ),
        ],
    )
    def post(self, request):
        serializer = RegisterSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        user = serializer.save()

        return Response(
            {
                "id": user.id,
                "name": user.name,
                "email": user.email,
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=LoginSerializer,
        responses={
            200: OpenApiResponse(
                description=(
                    "Login successful. Returns JWT tokens "
                    "and user information."
                ),
                examples=[
                    OpenApiExample(
                        "Login Success",
                        value={
                            "refresh": "refresh-token",
                            "access": "access-token",
                            "user": {
                                "id": 1,
                                "name": "John Doe",
                                "email": "john@example.com",
                            },
                        },
                        response_only=True,
                    ),
                ],
            ),
        },
        examples=[
            OpenApiExample(
                "Login Request",
                value={
                    "email": "john@example.com",
                    "password": "Password@123",
                },
                request_only=True,
            ),
        ],
    )
    def post(self, request):
        serializer = LoginSerializer(
            data=request.data,
            context={"request": request},
        )

        serializer.is_valid(
            raise_exception=True
        )

        return Response(
            serializer.validated_data,
            status=status.HTTP_200_OK,
        )


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=LogoutSerializer,
        responses={
            205: OpenApiResponse(
                description=(
                    "Refresh token successfully blacklisted."
                )
            ),
            400: OpenApiResponse(
                description=(
                    "Invalid or missing refresh token."
                )
            ),
        },
        examples=[
            OpenApiExample(
                "Logout Request",
                value={
                    "refresh": "your-refresh-token",
                },
                request_only=True,
            ),
        ],
    )
    def post(self, request):
        serializer = LogoutSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        refresh_token = serializer.validated_data["refresh"]

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()

        except TokenError:
            return Response(
                {
                    "error": {
                        "code": "INVALID_REFRESH_TOKEN",
                        "message": (
                            "Invalid or expired refresh token."
                        ),
                    }
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            status=status.HTTP_205_RESET_CONTENT
        )