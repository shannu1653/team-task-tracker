from django.urls import path

from .views import (
    ProjectTaskListCreateView,
    TaskDetailView,
)


urlpatterns = [
    # Project task list and creation
    path(
        "projects/<int:project_id>/tasks/",
        ProjectTaskListCreateView.as_view(),
        name="project-task-list-create",
    ),

    # Individual task retrieve, update, and delete
    path(
        "tasks/<int:task_id>/",
        TaskDetailView.as_view(),
        name="task-detail",
    ),
]