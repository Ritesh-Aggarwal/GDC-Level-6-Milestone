from http import HTTPStatus

from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient
from tasks.models import Task


class ApiViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="bruce_wayne", password="i_am_batman")
        self.user.save()

    def test_authentication(self):
        res = self.client.get("/api/")
        self.assertFalse(res.status_code==200)

    def test_tasks_view(self):
        self.client.login(username="bruce_wayne", password="i_am_batman")
        res = self.client.get("/api/")
        self.assertEquals(res.status_code, 200)

    def test_detail_view_task(self):
        self.client.login(username="bruce_wayne", password="i_am_batman")
        obj = Task.objects.create(
            title="test task",
            description="this is a task for testing",
            priority=1,
            user=self.user,
        )
        obj.save()

        res = self.client.get(f"/api/{obj.id}/")
        self.assertEqual(res.status_code, HTTPStatus.OK)

        res = self.client.get(f"/api/{obj.id}/history/")
        self.assertEqual(res.status_code, HTTPStatus.OK)

        res = self.client.get(f"/api/{obj.id}/history/1/")
        self.assertEqual(res.status_code, HTTPStatus.OK)

    def test_history_view(self):
        self.client.login(username="bruce_wayne", password="i_am_batman")
        res = self.client.get("/historyapi/")
        self.assertEquals(res.status_code, HTTPStatus.OK)
