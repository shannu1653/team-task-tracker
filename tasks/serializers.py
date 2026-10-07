from rest_framework import serializers

from accounts.models import User
from projects.models import Project, ProjectMembership

from .models import Task


class TaskCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = (
            "id",
            "title",
            "description",
            "priority",
            "status",
            "due_date",
            "assignee",
            "created_by",
            "created_at",
            "updated_at",
            "completed_at",
        )

        read_only_fields = (
            "id",
            "created_by",
            "created_at",
            "updated_at",
            "completed_at",
        )

    def validate_title(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Task title cannot be blank."
            )

        return value

    def validate_priority(self, value):
        valid_priorities = {
            Task.Priority.LOW,
            Task.Priority.MEDIUM,
            Task.Priority.HIGH,
        }

        if value not in valid_priorities:
            raise serializers.ValidationError(
                "Priority must be LOW, MEDIUM, or HIGH."
            )

        return value

    def validate_status(self, value):
        valid_statuses = {
            Task.Status.TODO,
            Task.Status.IN_PROGRESS,
            Task.Status.DONE,
        }

        if value not in valid_statuses:
            raise serializers.ValidationError(
                "Status must be TODO, IN_PROGRESS, or DONE."
            )

        return value

    def validate_assignee(self, value):
        project = self.context["project"]

        is_member = ProjectMembership.objects.filter(
            project=project,
            user=value,
        ).exists()

        if not is_member:
            raise serializers.ValidationError(
                "Assignee must be a member of this project."
            )

        return value

    def create(self, validated_data):
        project = self.context["project"]
        user = self.context["request"].user

        return Task.objects.create(
            project=project,
            created_by=user,
            **validated_data,
        )

class TaskListSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(
        source="created_by.name",
        read_only=True,
    )

    assignee_name = serializers.CharField(
        source="assignee.name",
        read_only=True,
        allow_null=True,
    )

    class Meta:
        model = Task
        fields = (
            "id",
            "title",
            "description",
            "priority",
            "status",
            "due_date",
            "assignee",
            "assignee_name",
            "created_by",
            "created_by_name",
            "created_at",
            "updated_at",
            "completed_at",
        )

