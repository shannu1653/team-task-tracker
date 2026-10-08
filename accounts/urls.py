from django.urls import path

from .views import (
    RegisterView,
    LoginView,
    LogoutView,
)


urlpatterns = [
    # User registration
    path(
        "register/",
        RegisterView.as_view(),
        name="register",
    ),

    # JWT login
    path(
        "login/",
        LoginView.as_view(),
        name="login",
    ),

    # JWT refresh-token logout / blacklist
    path(
        "logout/",
        LogoutView.as_view(),
        name="logout",
    ),
]