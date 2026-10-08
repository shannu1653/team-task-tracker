from django.db import transaction
from rest_framework import serializers

from accounts.models import User

from .models import Project, ProjectMembership


class ProjectCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = (
            "id",
            "name",
            "description",
            "owner",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "owner",
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

    def validate_description(self, value):
        return value.strip()

    @transaction.atomic
    def create(self, validated_data):
        request = self.context["request"]

        project = Project.objects.create(
            name=validated_data["name"],
            description=validated_data.get(
                "description",
                "",
            ),
            owner=request.user,
        )

        ProjectMembership.objects.create(
            project=project,
            user=request.user,
        )

        return project


class ProjectListSerializer(serializers.ModelSerializer):
    owner_name = serializers.CharField(
        source="owner.name",
        read_only=True,
    )

    member_count = serializers.IntegerField(
        read_only=True,
    )

    task_count = serializers.IntegerField(
        read_only=True,
    )

    class Meta:
        model = Project
        fields = (
            "id",
            "name",
            "description",
            "owner",
            "owner_name",
            "member_count",
            "task_count",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "owner",
            "owner_name",
            "member_count",
            "task_count",
            "created_at",
            "updated_at",
        )


class AddProjectMemberSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        value = value.strip().lower()

        if not User.objects.filter(
            email__iexact=value
        ).exists():
            raise serializers.ValidationError(
                "User with this email does not exist."
            )

        return value

    def save(self, **kwargs):
        project = self.context["project"]

        user = User.objects.get(
            email__iexact=self.validated_data["email"]
        )

        if ProjectMembership.objects.filter(
            project=project,
            user=user,
        ).exists():
            raise serializers.ValidationError(
                "User is already a member of this project."
            )

        return ProjectMembership.objects.create(
            project=project,
            user=user,
        )


class ProjectMemberSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(
        source="user.id",
        read_only=True,
    )

    name = serializers.CharField(
        source="user.name",
        read_only=True,
    )

    email = serializers.EmailField(
        source="user.email",
        read_only=True,
    )

    class Meta:
        model = ProjectMembership
        fields = (
            "user_id",
            "name",
            "email",
            "joined_at",
        )
        read_only_fields = fields