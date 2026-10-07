from django.db import transaction
from rest_framework import serializers

from .models import Project, ProjectMembership

from accounts.models import User


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

class ProjectListSerializer(serializers.ModelSerializer):
    owner_name = serializers.CharField(
        source="owner.name",
        read_only=True,
    )

    class Meta:
        model = Project
        fields = (
            "id",
            "name",
            "description",
            "owner_name",
            "created_at",
            "updated_at",
        )

class AddProjectMemberSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        value = value.strip().lower()

        if not User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("User with this email does not exist.")

        return value

    def save(self, **kwargs):
        project = self.context["project"]
        user = User.objects.get(email__iexact=self.validated_data["email"])

        if ProjectMembership.objects.filter(
            project=project,
            user=user
        ).exists():
            raise serializers.ValidationError(
                "User is already a member of this project."
            )

        membership = ProjectMembership.objects.create(
            project=project,
            user=user,
        )

        return membership