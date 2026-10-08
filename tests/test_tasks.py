from datetime import timedelta

from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User
from audit.models import AuditLog
from projects.models import Project, ProjectMembership
from tasks.models import Task


class TaskAPITests(APITestCase):
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

        self.non_member = User.objects.create_user(
            email="nonmember@example.com",
            name="Non Member",
            password="Password@123",
        )

        self.project = Project.objects.create(
            name="Task Project",
            description="Task testing project",
            owner=self.owner,
        )

        ProjectMembership.objects.create(
            project=self.project,
            user=self.owner,
        )

        ProjectMembership.objects.create(
            project=self.project,
            user=self.member,
        )

        self.client.force_authenticate(
            user=self.member
        )

    def create_task(self, **overrides):
        data = {
            "title": "Build API",
            "description": "Implement the task API",
            "priority": "HIGH",
            "status": "TODO",
        }

        data.update(overrides)

        return self.client.post(
            f"/projects/{self.project.id}/tasks/",
            data,
            format="json",
        )

    def test_member_can_create_task(self):
        response = self.create_task()

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        task = Task.objects.get(
            id=response.data["id"]
        )

        self.assertEqual(
            task.project,
            self.project,
        )

        self.assertEqual(
            task.created_by,
            self.member,
        )

        self.assertEqual(
            task.priority,
            Task.Priority.HIGH,
        )

        self.assertTrue(
            AuditLog.objects.filter(
                action=AuditLog.Action.TASK_CREATED,
                task=task,
                user=self.member,
            ).exists()
        )

    def test_non_member_cannot_create_task(self):
        self.client.force_authenticate(
            user=self.non_member
        )

        response = self.create_task()

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_assignee_must_be_project_member(self):
        response = self.create_task(
            assignee=self.non_member.id
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertEqual(
            Task.objects.count(),
            0,
        )

    def test_member_can_update_task(self):
        task = Task.objects.create(
            project=self.project,
            title="Old title",
            description="Old description",
            priority=Task.Priority.MEDIUM,
            status=Task.Status.TODO,
            created_by=self.member,
        )

        response = self.client.patch(
            f"/tasks/{task.id}/",
            {
                "title": "Updated title",
                "priority": "HIGH",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        task.refresh_from_db()

        self.assertEqual(
            task.title,
            "Updated title",
        )

        self.assertEqual(
            task.priority,
            Task.Priority.HIGH,
        )

        self.assertTrue(
            AuditLog.objects.filter(
                action=AuditLog.Action.TASK_UPDATED,
                task=task,
                user=self.member,
            ).exists()
        )

    def test_non_member_cannot_update_task(self):
        task = Task.objects.create(
            project=self.project,
            title="Protected task",
            created_by=self.member,
            status=Task.Status.TODO,
        )

        self.client.force_authenticate(
            user=self.non_member
        )

        response = self.client.patch(
            f"/tasks/{task.id}/",
            {
                "title": "Unauthorized update",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

        task.refresh_from_db()

        self.assertEqual(
            task.title,
            "Protected task",
        )

    def test_completed_at_is_set_when_task_becomes_done(self):
        task = Task.objects.create(
            project=self.project,
            title="Finish task",
            created_by=self.member,
            status=Task.Status.TODO,
        )

        response = self.client.patch(
            f"/tasks/{task.id}/",
            {
                "status": "DONE"
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        task.refresh_from_db()

        self.assertIsNotNone(
            task.completed_at
        )

    def test_completed_at_is_cleared_when_task_is_reopened(self):
        completed_time = timezone.now()

        task = Task.objects.create(
            project=self.project,
            title="Reopen task",
            created_by=self.member,
            status=Task.Status.DONE,
            completed_at=completed_time,
        )

        response = self.client.patch(
            f"/tasks/{task.id}/",
            {
                "status": "IN_PROGRESS"
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        task.refresh_from_db()

        self.assertIsNone(
            task.completed_at
        )

    def test_invalid_status_and_priority_are_rejected(self):
        invalid_status_response = self.create_task(
            status="INVALID_STATUS"
        )

        self.assertEqual(
            invalid_status_response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        invalid_priority_response = self.create_task(
            priority="INVALID_PRIORITY"
        )

        self.assertEqual(
            invalid_priority_response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertEqual(
            Task.objects.count(),
            0,
        )

    def test_task_list_supports_filters_and_sorting(self):
        Task.objects.create(
            project=self.project,
            title="Low task",
            created_by=self.member,
            priority=Task.Priority.LOW,
            status=Task.Status.TODO,
            due_date=timezone.now() + timedelta(days=3),
        )

        high_task = Task.objects.create(
            project=self.project,
            title="High task",
            created_by=self.member,
            priority=Task.Priority.HIGH,
            status=Task.Status.IN_PROGRESS,
            due_date=timezone.now() + timedelta(days=1),
        )

        response = self.client.get(
            f"/projects/{self.project.id}/tasks/",
            {
                "priority": "HIGH",
                "status": "IN_PROGRESS",
                "sort": "due_date",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["total"],
            1,
        )

        self.assertEqual(
            response.data["results"][0]["id"],
            high_task.id,
        )

    def test_task_list_supports_due_date_range_filter(self):
        now = timezone.now()

        early_task = Task.objects.create(
            project=self.project,
            title="Early task",
            created_by=self.member,
            due_date=now + timedelta(days=1),
        )

        late_task = Task.objects.create(
            project=self.project,
            title="Late task",
            created_by=self.member,
            due_date=now + timedelta(days=5),
        )

        response = self.client.get(
            f"/projects/{self.project.id}/tasks/",
            {
                "due_from": (
                    now + timedelta(hours=12)
                ).isoformat(),
                "due_to": (
                    now + timedelta(days=2)
                ).isoformat(),
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        result_ids = [
            item["id"]
            for item in response.data["results"]
        ]

        self.assertIn(
            early_task.id,
            result_ids,
        )

        self.assertNotIn(
            late_task.id,
            result_ids,
        )

    def test_task_list_pagination_defaults_to_ten(self):
        for index in range(12):
            Task.objects.create(
                project=self.project,
                title=f"Task {index}",
                created_by=self.member,
            )

        response = self.client.get(
            f"/projects/{self.project.id}/tasks/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["page_size"],
            10,
        )

        self.assertEqual(
            response.data["total"],
            12,
        )

        self.assertEqual(
            len(response.data["results"]),
            10,
        )

    def test_task_list_max_page_size_is_fifty(self):
        for index in range(55):
            Task.objects.create(
                project=self.project,
                title=f"Task {index}",
                created_by=self.member,
            )

        response = self.client.get(
            f"/projects/{self.project.id}/tasks/",
            {
                "page_size": 100,
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["page_size"],
            50,
        )

        self.assertEqual(
            len(response.data["results"]),
            50,
        )

    def test_project_summary_returns_task_counts(self):
        Task.objects.create(
            project=self.project,
            title="Todo task",
            created_by=self.member,
            status=Task.Status.TODO,
            priority=Task.Priority.LOW,
        )

        Task.objects.create(
            project=self.project,
            title="Done task",
            created_by=self.member,
            status=Task.Status.DONE,
            priority=Task.Priority.HIGH,
        )

        response = self.client.get(
            f"/projects/{self.project.id}/summary/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["total_tasks"],
            2,
        )

        self.assertEqual(
            response.data["status_counts"]["TODO"],
            1,
        )

        self.assertEqual(
            response.data["status_counts"]["DONE"],
            1,
        )

        self.assertEqual(
            response.data["priority_counts"]["LOW"],
            1,
        )

        self.assertEqual(
            response.data["priority_counts"]["HIGH"],
            1,
        )

    def test_task_creator_can_delete_task(self):
        task = Task.objects.create(
            project=self.project,
            title="Delete me",
            created_by=self.member,
        )

        response = self.client.delete(
            f"/tasks/{task.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

        self.assertFalse(
            Task.objects.filter(
                id=task.id
            ).exists()
        )

        self.assertTrue(
            AuditLog.objects.filter(
                action=AuditLog.Action.TASK_DELETED,
                user=self.member,
                project=self.project,
            ).exists()
        )

    def test_only_creator_or_owner_can_delete_task(self):
        task = Task.objects.create(
            project=self.project,
            title="Protected delete",
            created_by=self.owner,
        )

        self.client.force_authenticate(
            user=self.member
        )

        response = self.client.delete(
            f"/tasks/{task.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        self.assertTrue(
            Task.objects.filter(
                id=task.id
            ).exists()
        )