from django.utils import timezone
from rest_framework import serializers

from projects.models import ProjectMembership

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

    def validate_description(self, value):
        return value.strip()

    def validate_assignee(self, value):
        if value is None:
            return value

        project = self.context["project"]

        is_member = ProjectMembership.objects.filter(
            project=project,
            user=value,
        ).exists()

        if not is_member:
            raise serializers.ValidationError(
                "Assignee must be a member of the project."
            )

        return value

    def create(self, validated_data):
        request = self.context["request"]
        project = self.context["project"]

        return Task.objects.create(
            project=project,
            created_by=request.user,
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
        read_only_fields = (
            "id",
            "created_by",
            "created_by_name",
            "assignee_name",
            "created_at",
            "updated_at",
            "completed_at",
        )


class TaskUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = (
            "title",
            "description",
            "priority",
            "status",
            "due_date",
            "assignee",
        )

    def validate_title(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Task title cannot be blank."
            )

        return value

    def validate_description(self, value):
        return value.strip()

    def validate_assignee(self, value):
        if value is None:
            return value

        project = self.context["project"]

        is_member = ProjectMembership.objects.filter(
            project=project,
            user=value,
        ).exists()

        if not is_member:
            raise serializers.ValidationError(
                "Assignee must be a member of the project."
            )

        return value

    def update(self, instance, validated_data):
        old_status = instance.status

        new_status = validated_data.get(
            "status",
            instance.status,
        )

        for attribute, value in validated_data.items():
            setattr(
                instance,
                attribute,
                value,
            )

        # First transition to DONE.
        if (
            old_status != Task.Status.DONE
            and new_status == Task.Status.DONE
        ):
            instance.completed_at = timezone.now()

        # Reopen a completed task.
        elif (
            old_status == Task.Status.DONE
            and new_status != Task.Status.DONE
        ):
            instance.completed_at = None

        instance.save()

        return instance