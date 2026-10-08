from django.conf import settings
from django.db import models


class Project(models.Model):
    name = models.CharField(
        max_length=200,
    )

    description = models.TextField(
        blank=True,
    )

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="owned_projects",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["-created_at"]

        indexes = [
            models.Index(
                fields=["owner"],
                name="project_owner_idx",
            ),
            models.Index(
                fields=["created_at"],
                name="project_created_idx",
            ),
        ]

    def __str__(self):
        return self.name


class ProjectMembership(models.Model):
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="memberships",
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="project_memberships",
    )

    joined_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["joined_at"]

        constraints = [
            models.UniqueConstraint(
                fields=["project", "user"],
                name="unique_project_member",
            ),
        ]

        indexes = [
            models.Index(
                fields=["project", "user"],
                name="project_member_lookup_idx",
            ),
            models.Index(
                fields=["user"],
                name="project_member_user_idx",
            ),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.project.name}"