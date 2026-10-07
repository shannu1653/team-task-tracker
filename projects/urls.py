from django.urls import path

from .views import (
    ProjectListCreateView,
    ProjectDetailView,
    ProjectMemberCreateView,
)


urlpatterns = [
    path(
        "",
        ProjectListCreateView.as_view(),
        name="project-list-create",
    ),
    path(
        "<int:project_id>/",
        ProjectDetailView.as_view(),
        name="project-detail",
    ),
    path(
        "<int:project_id>/members/",
        ProjectMemberCreateView.as_view(),
        name="project-member-create",
    ),
]