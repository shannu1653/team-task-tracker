from django.db import transaction
from rest_framework import serializers

from .models import Project, ProjectMembership


class ProjectCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = (
            "id",
            "name",
            "description",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
        )

    def validate_name(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Project name cannot be blank."
            )

        return value

    @transaction.atomic
    def create(self, validated_data):
        user = self.context["request"].user

        project = Project.objects.create(
            owner=user,
            **validated_data,
        )

        ProjectMembership.objects.create(
            project=project,
            user=user,
        )

        return project