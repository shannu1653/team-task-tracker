from .models import ProjectMembership


def is_project_member(user, project):
    return ProjectMembership.objects.filter(
        project=project,
        user=user,
    ).exists()