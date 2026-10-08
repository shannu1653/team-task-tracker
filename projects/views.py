from django.db import transaction
from django.db.models import Count
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiResponse,
    extend_schema,
)
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from audit.models import AuditLog
from audit.services import create_audit_log

from .models import Project, ProjectMembership
from .serializers import (
    AddProjectMemberSerializer,
    ProjectCreateSerializer,
    ProjectListSerializer,
    ProjectMemberSerializer,
)


class ProjectListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=ProjectCreateSerializer,
        responses={
            201: ProjectCreateSerializer,
        },
        examples=[
            OpenApiExample(
                "Create Project",
                value={
                    "name": "Website Project",
                    "description": "Team website development",
                },
                request_only=True,
            ),
        ],
    )
    def post(self, request):
        serializer = ProjectCreateSerializer(
            data=request.data,
            context={"request": request},
        )

        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            project = serializer.save()

            create_audit_log(
                user=request.user,
                action=AuditLog.Action.PROJECT_CREATED,
                project=project,
                details={
                    "project_id": project.id,
                    "project_name": project.name,
                },
            )

        return Response(
            ProjectCreateSerializer(
                project,
                context={"request": request},
            ).data,
            status=status.HTTP_201_CREATED,
        )

    @extend_schema(
        responses={
            200: ProjectListSerializer(many=True),
        },
    )
    def get(self, request):
        projects = (
            Project.objects.filter(
                memberships__user=request.user,
            )
            .select_related("owner")
            .prefetch_related(
                "memberships",
                "tasks",
            )
            .annotate(
                member_count=Count(
                    "memberships",
                    distinct=True,
                ),
                task_count=Count(
                    "tasks",
                    distinct=True,
                ),
            )
            .distinct()
        )

        serializer = ProjectListSerializer(
            projects,
            many=True,
        )

        return Response(serializer.data)


class ProjectDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={
            200: ProjectListSerializer,
            404: OpenApiResponse(
                description="Project not found.",
            ),
        },
    )
    def get(self, request, project_id):
        project = (
            Project.objects.filter(
                id=project_id,
                memberships__user=request.user,
            )
            .select_related("owner")
            .prefetch_related(
                "memberships",
                "tasks",
            )
            .annotate(
                member_count=Count(
                    "memberships",
                    distinct=True,
                ),
                task_count=Count(
                    "tasks",
                    distinct=True,
                ),
            )
            .first()
        )

        if not project:
            return Response(
                {
                    "error": {
                        "code": "NOT_FOUND",
                        "message": "Project not found.",
                    }
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ProjectListSerializer(project)

        return Response(serializer.data)

    @extend_schema(
        responses={
            204: OpenApiResponse(
                description="Project deleted successfully.",
            ),
            403: OpenApiResponse(
                description="Only the project owner can delete the project.",
            ),
            404: OpenApiResponse(
                description="Project not found.",
            ),
        },
    )
    def delete(self, request, project_id):
        project = (
            Project.objects.filter(
                id=project_id,
                memberships__user=request.user,
            )
            .first()
        )

        if not project:
            return Response(
                {
                    "error": {
                        "code": "NOT_FOUND",
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
                        "message": (
                            "Only the project owner can delete "
                            "the project."
                        ),
                    }
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        project_id_value = project.id
        project_name = project.name

        with transaction.atomic():
            create_audit_log(
                user=request.user,
                action=AuditLog.Action.PROJECT_DELETED,
                project=project,
                details={
                    "project_id": project_id_value,
                    "project_name": project_name,
                },
            )

            project.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT,
        )


class ProjectMemberListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get_project(self, request, project_id):
        return (
            Project.objects.filter(
                id=project_id,
                memberships__user=request.user,
            )
            .select_related("owner")
            .first()
        )

    @extend_schema(
        responses={
            200: ProjectMemberSerializer(many=True),
            404: OpenApiResponse(
                description="Project not found.",
            ),
        },
    )
    def get(self, request, project_id):
        project = self.get_project(
            request,
            project_id,
        )

        if not project:
            return Response(
                {
                    "error": {
                        "code": "NOT_FOUND",
                        "message": "Project not found.",
                    }
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        members = (
            ProjectMembership.objects.filter(
                project=project,
            )
            .select_related("user")
        )

        serializer = ProjectMemberSerializer(
            members,
            many=True,
        )

        return Response(serializer.data)

    @extend_schema(
        request=AddProjectMemberSerializer,
        responses={
            201: ProjectMemberSerializer,
            403: OpenApiResponse(
                description="Only the project owner can add members.",
            ),
            404: OpenApiResponse(
                description="Project not found.",
            ),
        },
        examples=[
            OpenApiExample(
                "Add Member",
                value={
                    "email": "member@example.com",
                },
                request_only=True,
            ),
        ],
    )
    def post(self, request, project_id):
        project = self.get_project(
            request,
            project_id,
        )

        if not project:
            return Response(
                {
                    "error": {
                        "code": "NOT_FOUND",
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
                        "message": (
                            "Only the project owner can add members."
                        ),
                    }
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = AddProjectMemberSerializer(
            data=request.data,
            context={"project": project},
        )

        serializer.is_valid(
            raise_exception=True,
        )

        with transaction.atomic():
            membership = serializer.save()

            create_audit_log(
                user=request.user,
                action=AuditLog.Action.MEMBER_ADDED,
                project=project,
                details={
                    "member_id": membership.user_id,
                    "member_email": membership.user.email,
                    "member_name": membership.user.name,
                },
            )

        return Response(
            ProjectMemberSerializer(membership).data,
            status=status.HTTP_201_CREATED,
        )


class ProjectSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={
            200: OpenApiResponse(
                description="Project task summary.",
                examples=[
                    OpenApiExample(
                        "Project Summary",
                        value={
                            "project_id": 1,
                            "project_name": "Website Project",
                            "total_tasks": 5,
                            "status_counts": {
                                "TODO": 2,
                                "IN_PROGRESS": 1,
                                "DONE": 2,
                            },
                            "priority_counts": {
                                "LOW": 1,
                                "MEDIUM": 2,
                                "HIGH": 2,
                            },
                        },
                        response_only=True,
                    ),
                ],
            ),
            404: OpenApiResponse(
                description="Project not found.",
            ),
        },
    )
    def get(self, request, project_id):
        project = (
            Project.objects.filter(
                id=project_id,
                memberships__user=request.user,
            )
            .first()
        )

        if not project:
            return Response(
                {
                    "error": {
                        "code": "NOT_FOUND",
                        "message": "Project not found.",
                    }
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        tasks = project.tasks.all()

        total_tasks = tasks.count()

        status_counts = {
            "TODO": tasks.filter(
                status="TODO",
            ).count(),
            "IN_PROGRESS": tasks.filter(
                status="IN_PROGRESS",
            ).count(),
            "DONE": tasks.filter(
                status="DONE",
            ).count(),
        }

        priority_counts = {
            "LOW": tasks.filter(
                priority="LOW",
            ).count(),
            "MEDIUM": tasks.filter(
                priority="MEDIUM",
            ).count(),
            "HIGH": tasks.filter(
                priority="HIGH",
            ).count(),
        }

        return Response(
            {
                "project_id": project.id,
                "project_name": project.name,
                "total_tasks": total_tasks,
                "status_counts": status_counts,
                "priority_counts": priority_counts,
            }
        )