from drf_spectacular.utils import extend_schema
from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Project
from .serializers import (
    AddProjectMemberSerializer,
    ProjectCreateSerializer,
    ProjectListSerializer,
)


class ProjectListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=ProjectCreateSerializer,
        responses={201: ProjectCreateSerializer},
    )
    def post(self, request):
        serializer = ProjectCreateSerializer(
            data=request.data,
            context={"request": request},
        )

        if serializer.is_valid():
            project = serializer.save()

            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
            )

        return Response(
            {
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Invalid project data.",
                    "details": serializer.errors,
                }
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    @extend_schema(
        responses=ProjectListSerializer(many=True),
    )
    def get(self, request):
        projects = (
            Project.objects
            .filter(memberships__user=request.user)
            .select_related("owner")
        )

        serializer = ProjectListSerializer(
            projects,
            many=True,
        )

        return Response(serializer.data)


class ProjectDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses=ProjectListSerializer,
    )
    def get(self, request, project_id):
        project = (
            Project.objects
            .filter(
                id=project_id,
                memberships__user=request.user,
            )
            .select_related("owner")
            .first()
        )

        if project is None:
            return Response(
                {
                    "error": {
                        "code": "PROJECT_NOT_FOUND",
                        "message": "Project not found.",
                    }
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ProjectListSerializer(project)

        return Response(serializer.data)

    def delete(self, request, project_id):
        project = (
            Project.objects
            .filter(
                id=project_id,
                memberships__user=request.user,
            )
            .first()
        )

        if project is None:
            return Response(
                {
                    "error": {
                        "code": "PROJECT_NOT_FOUND",
                        "message": "Project not found.",
                    }
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if project.owner_id != request.user.id:
            return Response(
                {
                    "error": {
                        "code": "FORBIDDEN",
                        "message": "Only the project owner can delete the project.",
                    }
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        project.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class ProjectMemberCreateView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=AddProjectMemberSerializer,
        responses={201: AddProjectMemberSerializer},
    )
    def post(self, request, project_id):
        project = Project.objects.filter(id=project_id).first()

        if project is None:
            return Response(
                {
                    "error": {
                        "code": "PROJECT_NOT_FOUND",
                        "message": "Project not found.",
                    }
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if project.owner_id != request.user.id:
            return Response(
                {
                    "error": {
                        "code": "FORBIDDEN",
                        "message": "Only the project owner can add members.",
                    }
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = AddProjectMemberSerializer(
            data=request.data,
            context={"project": project},
        )

        if serializer.is_valid():
            try:
                membership = serializer.save()
            except serializers.ValidationError as exc:
                return Response(
                    {
                        "error": {
                            "code": "MEMBER_ALREADY_EXISTS",
                            "message": str(exc.detail[0]),
                        }
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user = membership.user

            return Response(
                {
                    "id": user.id,
                    "name": user.name,
                    "email": user.email,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            {
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Invalid member data.",
                    "details": serializer.errors,
                }
            },
            status=status.HTTP_400_BAD_REQUEST,
        )