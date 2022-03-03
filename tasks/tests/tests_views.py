from http import HTTPStatus

from django.contrib.auth.models import AnonymousUser, User
from django.test import RequestFactory, TestCase
from tasks.views import GenericListView


class GenericViewTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username="bruce_wayne",  password="i_am_batman")

    def test_user_signup_view(self):
        response =  self.client.get('/user/signup')
        self.assertEqual(response.status_code, 200)
    
    def test_user_login_view(self):
        response =  self.client.get('/user/login')
        self.assertEqual(response.status_code, 200)

    def test_user_logout_view(self):
        res = self.client.get("/user/logout/")
        self.assertEquals(res.status_code, HTTPStatus.FOUND)
        self.assertEquals(res.url, "/user/login")

    def test_authenticated(self):
        request = self.factory.get("/tasks")
        request.user = self.user
        response = GenericListView.as_view()(request)
        self.assertEqual(response.status_code, 200)

    # completed view authentication test
    def test_completed_view(self):
        request = self.factory.get("/completed_tasks/")
        request.user = self.user
        response = GenericListView.as_view()(request)
        self.assertEqual(response.status_code, 200)
    
    # all task view authentication test
    def test_alltask_view(self):
        request = self.factory.get("/all_tasks/")
        request.user = self.user
        response = GenericListView.as_view()(request)
        self.assertEqual(response.status_code, 200)

    def test_unauthenticated(self):
        request = self.factory.get("/tasks")
        request.user = AnonymousUser() 
        response = GenericListView.as_view()(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/user/login?next=/tasks')



