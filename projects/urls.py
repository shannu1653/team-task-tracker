from django.urls import path

from .views import (
    ProjectDetailView,
    ProjectListCreateView,
    ProjectMemberListCreateView,
    ProjectSummaryView,
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
        ProjectMemberListCreateView.as_view(),
        name="project-member-list-create",
    ),

    path(
        "<int:project_id>/summary/",
        ProjectSummaryView.as_view(),
        name="project-summary",
    ),
]