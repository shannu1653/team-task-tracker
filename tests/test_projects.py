from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User
from audit.models import AuditLog
from projects.models import Project, ProjectMembership


class ProjectAPITests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            email="owner@example.com",
            name="Owner",
            password="Password@123",
        )

        self.member = User.objects.create_user(
            email="member@example.com",
            name="Member",
            password="Password@123",
        )

        self.other_user = User.objects.create_user(
            email="other@example.com",
            name="Other User",
            password="Password@123",
        )

        self.client.force_authenticate(
            user=self.owner
        )

    def test_create_project_adds_creator_as_member(self):
        response = self.client.post(
            "/projects/",
            {
                "name": "Website Project",
                "description": "Team website",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        project = Project.objects.get(
            id=response.data["id"]
        )

        self.assertEqual(
            project.owner,
            self.owner,
        )

        self.assertTrue(
            ProjectMembership.objects.filter(
                project=project,
                user=self.owner,
            ).exists()
        )

        self.assertTrue(
            AuditLog.objects.filter(
                action=AuditLog.Action.PROJECT_CREATED,
                project=project,
                user=self.owner,
            ).exists()
        )

    def test_create_project_with_blank_name_is_rejected(self):
        response = self.client.post(
            "/projects/",
            {
                "name": "   ",
                "description": "Invalid project",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertEqual(
            Project.objects.count(),
            0,
        )

    def test_member_can_view_project(self):
        project = Project.objects.create(
            name="Website Project",
            description="Team website",
            owner=self.owner,
        )

        ProjectMembership.objects.create(
            project=project,
            user=self.owner,
        )

        ProjectMembership.objects.create(
            project=project,
            user=self.member,
        )

        self.client.force_authenticate(
            user=self.member
        )

        response = self.client.get(
            f"/projects/{project.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["id"],
            project.id,
        )

    def test_non_member_cannot_view_project(self):
        project = Project.objects.create(
            name="Private Project",
            owner=self.owner,
        )

        ProjectMembership.objects.create(
            project=project,
            user=self.owner,
        )

        self.client.force_authenticate(
            user=self.other_user
        )

        response = self.client.get(
            f"/projects/{project.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_only_owner_can_add_project_member(self):
        project = Project.objects.create(
            name="Team Project",
            owner=self.owner,
        )

        ProjectMembership.objects.create(
            project=project,
            user=self.owner,
        )

        ProjectMembership.objects.create(
            project=project,
            user=self.member,
        )

        self.client.force_authenticate(
            user=self.member
        )

        response = self.client.post(
            f"/projects/{project.id}/members/",
            {
                "email": self.other_user.email,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_owner_can_add_existing_user_as_member(self):
        project = Project.objects.create(
            name="Team Project",
            owner=self.owner,
        )

        ProjectMembership.objects.create(
            project=project,
            user=self.owner,
        )

        response = self.client.post(
            f"/projects/{project.id}/members/",
            {
                "email": self.member.email,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertTrue(
            ProjectMembership.objects.filter(
                project=project,
                user=self.member,
            ).exists()
        )

        self.assertTrue(
            AuditLog.objects.filter(
                action=AuditLog.Action.MEMBER_ADDED,
                project=project,
                user=self.owner,
            ).exists()
        )

    def test_duplicate_project_member_is_rejected(self):
        project = Project.objects.create(
            name="Team Project",
            owner=self.owner,
        )

        ProjectMembership.objects.create(
            project=project,
            user=self.owner,
        )

        ProjectMembership.objects.create(
            project=project,
            user=self.member,
        )

        response = self.client.post(
            f"/projects/{project.id}/members/",
            {
                "email": self.member.email,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertEqual(
            ProjectMembership.objects.filter(
                project=project,
                user=self.member,
            ).count(),
            1,
        )

    def test_only_owner_can_delete_project(self):
        project = Project.objects.create(
            name="Team Project",
            owner=self.owner,
        )

        ProjectMembership.objects.create(
            project=project,
            user=self.owner,
        )

        ProjectMembership.objects.create(
            project=project,
            user=self.member,
        )

        self.client.force_authenticate(
            user=self.member
        )

        response = self.client.delete(
            f"/projects/{project.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        self.assertTrue(
            Project.objects.filter(
                id=project.id
            ).exists()
        )

    def test_owner_can_delete_project(self):
        project = Project.objects.create(
            name="Delete Project",
            description="Project to delete",
            owner=self.owner,
        )

        ProjectMembership.objects.create(
            project=project,
            user=self.owner,
        )

        response = self.client.delete(
            f"/projects/{project.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

        self.assertFalse(
            Project.objects.filter(
                id=project.id
            ).exists()
        )

        self.assertTrue(
            AuditLog.objects.filter(
                action=AuditLog.Action.PROJECT_DELETED,
                user=self.owner,
            ).exists()
        )