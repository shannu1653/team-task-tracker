from django.utils.dateparse import parse_datetime

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from projects.models import Project, ProjectMembership

from .models import Task
from .serializers import (
    TaskCreateSerializer,
    TaskListSerializer,
    TaskUpdateSerializer,
)


class TaskPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 50


class ProjectTaskListCreateView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = TaskPagination

    # ---------------------------------------------------------
    # POST /projects/{project_id}/tasks/
    # ---------------------------------------------------------
    @extend_schema(
        request=TaskCreateSerializer,
        responses={201: TaskCreateSerializer},
    )
    def post(self, request, project_id):
        project = Project.objects.filter(
            id=project_id
        ).first()

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

        is_member = ProjectMembership.objects.filter(
            project=project,
            user=request.user,
        ).exists()

        if not is_member:
            return Response(
                {
                    "error": {
                        "code": "FORBIDDEN",
                        "message": "You are not a member of this project.",
                    }
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = TaskCreateSerializer(
            data=request.data,
            context={
                "request": request,
                "project": project,
            },
        )

        if serializer.is_valid():
            task = serializer.save()

            return Response(
                TaskCreateSerializer(task).data,
                status=status.HTTP_201_CREATED,
            )

        return Response(
            {
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Invalid task data.",
                    "details": serializer.errors,
                }
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    # ---------------------------------------------------------
    # GET /projects/{project_id}/tasks/
    # ---------------------------------------------------------
    @extend_schema(
        responses=TaskListSerializer(many=True),
    )
    def get(self, request, project_id):
        project = Project.objects.filter(
            id=project_id
        ).first()

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

        is_member = ProjectMembership.objects.filter(
            project=project,
            user=request.user,
        ).exists()

        if not is_member:
            return Response(
                {
                    "error": {
                        "code": "FORBIDDEN",
                        "message": "You are not a member of this project.",
                    }
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        tasks = (
            Task.objects
            .filter(project=project)
            .select_related(
                "assignee",
                "created_by",
            )
        )

        # -----------------------------------------------------
        # Filter: status
        # -----------------------------------------------------
        status_filter = request.query_params.get("status")

        if status_filter:
            if status_filter not in {
                Task.Status.TODO,
                Task.Status.IN_PROGRESS,
                Task.Status.DONE,
            }:
                return Response(
                    {
                        "error": {
                            "code": "VALIDATION_ERROR",
                            "message": (
                                "status must be TODO, "
                                "IN_PROGRESS, or DONE."
                            ),
                        }
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            tasks = tasks.filter(
                status=status_filter
            )

        # -----------------------------------------------------
        # Filter: priority
        # -----------------------------------------------------
        priority_filter = request.query_params.get("priority")

        if priority_filter:
            if priority_filter not in {
                Task.Priority.LOW,
                Task.Priority.MEDIUM,
                Task.Priority.HIGH,
            }:
                return Response(
                    {
                        "error": {
                            "code": "VALIDATION_ERROR",
                            "message": (
                                "priority must be LOW, "
                                "MEDIUM, or HIGH."
                            ),
                        }
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            tasks = tasks.filter(
                priority=priority_filter
            )

        # -----------------------------------------------------
        # Filter: assignee
        # -----------------------------------------------------
        assignee_filter = request.query_params.get("assignee")

        if assignee_filter:
            try:
                assignee_id = int(assignee_filter)
            except ValueError:
                return Response(
                    {
                        "error": {
                            "code": "VALIDATION_ERROR",
                            "message": (
                                "Assignee must be a valid user ID."
                            ),
                        }
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            tasks = tasks.filter(
                assignee_id=assignee_id
            )

        # -----------------------------------------------------
        # Filter: due_from
        # -----------------------------------------------------
        due_from = request.query_params.get("due_from")

        if due_from:
            parsed_due_from = parse_datetime(due_from)

            if parsed_due_from is None:
                return Response(
                    {
                        "error": {
                            "code": "VALIDATION_ERROR",
                            "message": (
                                "due_from must be a valid "
                                "ISO datetime."
                            ),
                        }
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            tasks = tasks.filter(
                due_date__gte=parsed_due_from
            )

        # -----------------------------------------------------
        # Filter: due_to
        # -----------------------------------------------------
        due_to = request.query_params.get("due_to")

        if due_to:
            parsed_due_to = parse_datetime(due_to)

            if parsed_due_to is None:
                return Response(
                    {
                        "error": {
                            "code": "VALIDATION_ERROR",
                            "message": (
                                "due_to must be a valid "
                                "ISO datetime."
                            ),
                        }
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            tasks = tasks.filter(
                due_date__lte=parsed_due_to
            )

        # -----------------------------------------------------
        # Sorting
        # -----------------------------------------------------
        sort_by = request.query_params.get(
            "sort",
            "created_at",
        )

        sort_order = request.query_params.get(
            "order",
            "desc",
        )

        allowed_sort_fields = {
            "created_at": "created_at",
            "due_date": "due_date",
        }

        if sort_by not in allowed_sort_fields:
            return Response(
                {
                    "error": {
                        "code": "VALIDATION_ERROR",
                        "message": (
                            "sort must be created_at or due_date."
                        ),
                    }
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if sort_order not in {"asc", "desc"}:
            return Response(
                {
                    "error": {
                        "code": "VALIDATION_ERROR",
                        "message": (
                            "order must be asc or desc."
                        ),
                    }
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        ordering = allowed_sort_fields[sort_by]

        if sort_order == "desc":
            ordering = f"-{ordering}"

        tasks = tasks.order_by(ordering)

        # -----------------------------------------------------
        # Pagination
        # -----------------------------------------------------
        paginator = self.pagination_class()

        page = paginator.paginate_queryset(
            tasks,
            request,
            view=self,
        )

        serializer = TaskListSerializer(
            page,
            many=True,
        )

        return paginator.get_paginated_response(
            serializer.data
        )


class TaskDetailView(APIView):
    permission_classes = [IsAuthenticated]

    # ---------------------------------------------------------
    # PATCH /tasks/{task_id}/
    # ---------------------------------------------------------
    @extend_schema(
        request=TaskUpdateSerializer,
        responses={200: TaskListSerializer},
    )
    def patch(self, request, task_id):
        task = (
            Task.objects
            .select_related("project")
            .filter(id=task_id)
            .first()
        )

        if task is None:
            return Response(
                {
                    "error": {
                        "code": "TASK_NOT_FOUND",
                        "message": "Task not found.",
                    }
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        is_member = ProjectMembership.objects.filter(
            project=task.project,
            user=request.user,
        ).exists()

        if not is_member:
            return Response(
                {
                    "error": {
                        "code": "FORBIDDEN",
                        "message": "You are not a member of this project.",
                    }
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = TaskUpdateSerializer(
            task,
            data=request.data,
            partial=True,
            context={
                "request": request,
                "project": task.project,
            },
        )

        if serializer.is_valid():
            updated_task = serializer.save()

            return Response(
                TaskListSerializer(updated_task).data,
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Invalid task data.",
                    "details": serializer.errors,
                }
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    # ---------------------------------------------------------
    # DELETE /tasks/{task_id}/
    # ---------------------------------------------------------
    @extend_schema(
        responses={204: None},
    )
    def delete(self, request, task_id):
        task = (
            Task.objects
            .select_related(
                "project",
                "project__owner",
                "created_by",
            )
            .filter(id=task_id)
            .first()
        )

        if task is None:
            return Response(
                {
                    "error": {
                        "code": "TASK_NOT_FOUND",
                        "message": "Task not found.",
                    }
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        is_owner = (
            task.project.owner_id == request.user.id
        )

        is_creator = (
            task.created_by_id == request.user.id
        )

        if not is_owner and not is_creator:
            return Response(
                {
                    "error": {
                        "code": "FORBIDDEN",
                        "message": (
                            "Only the project owner or task creator "
                            "can delete this task."
                        ),
                    }
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        task.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )