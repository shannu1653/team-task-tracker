from django.contrib import admin

from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "action",
        "project",
        "task",
        "created_at",
    )

    list_filter = (
        "action",
        "created_at",
    )

    search_fields = (
        "user__email",
        "action",
        "project__name",
        "task__title",
    )

    readonly_fields = (
        "user",
        "action",
        "project",
        "task",
        "details",
        "created_at",
    )

    date_hierarchy = "created_at"

    ordering = (
        "-created_at",
    )