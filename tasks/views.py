from django.db import transaction
from django.utils.dateparse import parse_datetime

from drf_spectacular.utils import extend_schema
from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from audit.models import AuditLog
from audit.services import create_audit_log

from projects.models import Project

from .models import Task
from .serializers import (
    TaskCreateSerializer,
    TaskListSerializer,
    TaskUpdateSerializer,
)


class TaskPagination:
    page_size = 10
    max_page_size = 50

    def paginate_queryset(self, queryset, request):
        try:
            page = int(
                request.query_params.get(
                    "page",
                    1,
                )
            )

            page_size = int(
                request.query_params.get(
                    "page_size",
                    self.page_size,
                )
            )

        except (TypeError, ValueError):
            raise serializers.ValidationError(
                {
                    "page": "Page must be a valid integer.",
                    "page_size": (
                        "Page size must be a valid integer."
                    ),
                }
            )

        if page < 1:
            raise serializers.ValidationError(
                {
                    "page": (
                        "Page must be greater than 0."
                    )
                }
            )

        if page_size < 1:
            raise serializers.ValidationError(
                {
                    "page_size": (
                        "Page size must be greater than 0."
                    )
                }
            )

        page_size = min(
            page_size,
            self.max_page_size,
        )

        start = (page - 1) * page_size
        end = start + page_size

        total = queryset.count()

        return {
            "results": queryset[start:end],
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": (
                (total + page_size - 1) // page_size
                if total
                else 0
            ),
        }


class ProjectTaskListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=TaskCreateSerializer,
        responses={201: TaskListSerializer},
    )
    def post(self, request, project_id):
        project = Project.objects.filter(
            id=project_id,
            memberships__user=request.user,
        ).first()

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

        serializer = TaskCreateSerializer(
            data=request.data,
            context={
                "request": request,
                "project": project,
            },
        )

        serializer.is_valid(
            raise_exception=True
        )

        with transaction.atomic():
            task = serializer.save()

            create_audit_log(
                user=request.user,
                action=AuditLog.Action.TASK_CREATED,
                project=project,
                task=task,
                details={
                    "task_id": task.id,
                    "title": task.title,
                    "status": task.status,
                    "priority": task.priority,
                },
            )

        return Response(
            TaskListSerializer(task).data,
            status=status.HTTP_201_CREATED,
        )

    @extend_schema(
        responses=TaskListSerializer(many=True),
    )
    def get(self, request, project_id):
        project = Project.objects.filter(
            id=project_id,
            memberships__user=request.user,
        ).first()

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

        queryset = (
            Task.objects.filter(
                project=project
            )
            .select_related(
                "created_by",
                "assignee",
                "project",
            )
        )

        # ----------------------------------------------------
        # FILTERS
        # ----------------------------------------------------

        status_filter = request.query_params.get(
            "status"
        )

        priority_filter = request.query_params.get(
            "priority"
        )

        assignee_filter = request.query_params.get(
            "assignee"
        )

        due_from = request.query_params.get(
            "due_from"
        )

        due_to = request.query_params.get(
            "due_to"
        )

        # Status filter
        if status_filter:
            if status_filter not in Task.Status.values:
                return Response(
                    {
                        "error": {
                            "code": "VALIDATION_ERROR",
                            "message": "Invalid status.",
                        }
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            queryset = queryset.filter(
                status=status_filter
            )

        # Priority filter
        if priority_filter:
            if priority_filter not in Task.Priority.values:
                return Response(
                    {
                        "error": {
                            "code": "VALIDATION_ERROR",
                            "message": "Invalid priority.",
                        }
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            queryset = queryset.filter(
                priority=priority_filter
            )

        # Assignee filter
        if assignee_filter:
            try:
                assignee_id = int(
                    assignee_filter
                )

            except (TypeError, ValueError):
                return Response(
                    {
                        "error": {
                            "code": "VALIDATION_ERROR",
                            "message": (
                                "Assignee must be a valid "
                                "user ID."
                            ),
                        }
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            queryset = queryset.filter(
                assignee_id=assignee_id
            )

        # Due date from
        if due_from:
            parsed_due_from = parse_datetime(
                due_from
            )

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

            queryset = queryset.filter(
                due_date__gte=parsed_due_from
            )

        # Due date to
        if due_to:
            parsed_due_to = parse_datetime(
                due_to
            )

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

            queryset = queryset.filter(
                due_date__lte=parsed_due_to
            )

        # ----------------------------------------------------
        # SORTING
        # ----------------------------------------------------

        sort = request.query_params.get(
            "sort",
            "-created_at",
        )

        allowed_sorts = {
            "created_at": "created_at",
            "-created_at": "-created_at",
            "due_date": "due_date",
            "-due_date": "-due_date",
        }

        if sort not in allowed_sorts:
            return Response(
                {
                    "error": {
                        "code": "VALIDATION_ERROR",
                        "message": "Invalid sort field.",
                    }
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        queryset = queryset.order_by(
            allowed_sorts[sort]
        )

        # ----------------------------------------------------
        # PAGINATION
        # ----------------------------------------------------

        paginator = TaskPagination()

        paginated = paginator.paginate_queryset(
            queryset,
            request,
        )

        serializer = TaskListSerializer(
            paginated["results"],
            many=True,
        )

        return Response(
            {
                "page": paginated["page"],
                "page_size": paginated["page_size"],
                "total": paginated["total"],
                "total_pages": paginated["total_pages"],
                "results": serializer.data,
            }
        )


class TaskDetailView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TaskListSerializer

    def get_task(self, request, task_id):
        return (
            Task.objects.filter(
                id=task_id,
                project__memberships__user=request.user,
            )
            .select_related(
                "project",
                "created_by",
                "assignee",
            )
            .first()
        )

    # --------------------------------------------------------
    # GET TASK
    # --------------------------------------------------------

    @extend_schema(
        responses=TaskListSerializer,
    )
    def get(self, request, task_id):
        task = self.get_task(
            request,
            task_id,
        )

        if not task:
            return Response(
                {
                    "error": {
                        "code": "NOT_FOUND",
                        "message": "Task not found.",
                    }
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = TaskListSerializer(task)

        return Response(
            serializer.data
        )

    # --------------------------------------------------------
    # UPDATE TASK
    # --------------------------------------------------------

    @extend_schema(
        request=TaskUpdateSerializer,
        responses=TaskListSerializer,
    )
    def patch(self, request, task_id):
        task = self.get_task(
            request,
            task_id,
        )

        if not task:
            return Response(
                {
                    "error": {
                        "code": "NOT_FOUND",
                        "message": "Task not found.",
                    }
                },
                status=status.HTTP_404_NOT_FOUND,
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

        serializer.is_valid(
            raise_exception=True
        )

        with transaction.atomic():
            updated_task = serializer.save()

            create_audit_log(
                user=request.user,
                action=AuditLog.Action.TASK_UPDATED,
                project=updated_task.project,
                task=updated_task,
                details={
                    "task_id": updated_task.id,
                    "changed_fields": list(
                        request.data.keys()
                    ),
                    "status": updated_task.status,
                    "priority": updated_task.priority,
                },
            )

        return Response(
            TaskListSerializer(
                updated_task
            ).data
        )

    # --------------------------------------------------------
    # DELETE TASK
    # --------------------------------------------------------

    def delete(self, request, task_id):
        task = self.get_task(
            request,
            task_id,
        )

        if not task:
            return Response(
                {
                    "error": {
                        "code": "NOT_FOUND",
                        "message": "Task not found.",
                    }
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # Only task creator or project owner
        # can delete the task.
        if (
            task.created_by_id != request.user.id
            and task.project.owner_id != request.user.id
        ):
            return Response(
                {
                    "error": {
                        "code": "FORBIDDEN",
                        "message": (
                            "Only the task creator or "
                            "project owner can delete "
                            "the task."
                        ),
                    }
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        project = task.project

        task_id_value = task.id
        task_title = task.title

        with transaction.atomic():
            create_audit_log(
                user=request.user,
                action=AuditLog.Action.TASK_DELETED,
                project=project,
                task=task,
                details={
                    "task_id": task_id_value,
                    "title": task_title,
                },
            )

            task.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )