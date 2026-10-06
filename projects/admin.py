from django.contrib import admin

from .models import Project, ProjectMembership


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "owner",
        "created_at",
        "updated_at",
    )

    search_fields = (
        "name",
        "owner__email",
    )

    list_filter = (
        "created_at",
        "updated_at",
    )


@admin.register(ProjectMembership)
class ProjectMembershipAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "project",
        "user",
        "joined_at",
    )

    search_fields = (
        "project__name",
        "user__email",
    )

    list_filter = (
        "joined_at",
    )