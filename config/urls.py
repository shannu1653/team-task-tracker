"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views.
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)


urlpatterns = [
    # ========================================================
    # ADMIN
    # ========================================================

    path(
        "admin/",
        admin.site.urls,
    ),

    # ========================================================
    # AUTHENTICATION APIs
    # ========================================================

    path(
        "auth/",
        include("accounts.urls"),
    ),

    # ========================================================
    # PROJECT APIs
    # ========================================================

    path(
        "projects/",
        include("projects.urls"),
    ),

    # ========================================================
    # TASK APIs
    # ========================================================

    path(
        "",
        include("tasks.urls"),
    ),

    # ========================================================
    # OPENAPI / SWAGGER
    # ========================================================

    path(
        "api/schema/",
        SpectacularAPIView.as_view(),
        name="schema",
    ),

    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(
            url_name="schema",
        ),
        name="swagger-ui",
    ),
]


# ============================================================
# DEVELOPMENT MEDIA FILES
# ============================================================

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )