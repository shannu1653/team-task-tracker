from django.urls import path

from .views import (
    ProjectTaskListCreateView,
    TaskDetailView,
)


urlpatterns = [
    path(
        "projects/<int:project_id>/tasks/",
        ProjectTaskListCreateView.as_view(),
        name="project-task-list-create",
    ),
    path(
        "tasks/<int:task_id>/",
        TaskDetailView.as_view(),
        name="task-detail",
    ),
]