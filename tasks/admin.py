from django.contrib import admin

from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "project",
        "created_by",
        "assignee",
        "priority",
        "status",
        "due_date",
        "completed_at",
        "created_at",
        "updated_at",
    )

    list_filter = (
        "priority",
        "status",
        "created_at",
        "updated_at",
    )

    search_fields = (
        "title",
        "description",
        "project__name",
        "created_by__email",
        "assignee__email",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
        "completed_at",
    )

    list_select_related = (
        "project",
        "created_by",
        "assignee",
    )

    ordering = ("-created_at",)