from django.conf import settings
from django.db import models


class AuditLog(models.Model):
    class Action(models.TextChoices):
        PROJECT_CREATED = "PROJECT_CREATED", "Project Created"
        PROJECT_DELETED = "PROJECT_DELETED", "Project Deleted"
        MEMBER_ADDED = "MEMBER_ADDED", "Member Added"
        TASK_CREATED = "TASK_CREATED", "Task Created"
        TASK_UPDATED = "TASK_UPDATED", "Task Updated"
        TASK_DELETED = "TASK_DELETED", "Task Deleted"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
    )

    action = models.CharField(
        max_length=50,
        choices=Action.choices,
    )

    project = models.ForeignKey(
        "projects.Project",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
    )

    task = models.ForeignKey(
        "tasks.Task",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
    )

    details = models.JSONField(
        default=dict,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["-created_at"]

        indexes = [
            models.Index(
                fields=["user", "created_at"],
                name="audit_user_created_idx",
            ),
            models.Index(
                fields=["project", "created_at"],
                name="audit_project_created_idx",
            ),
            models.Index(
                fields=["task", "created_at"],
                name="audit_task_created_idx",
            ),
            models.Index(
                fields=["action", "created_at"],
                name="audit_action_created_idx",
            ),
        ]

    def __str__(self):
        return f"{self.action} - {self.user}"