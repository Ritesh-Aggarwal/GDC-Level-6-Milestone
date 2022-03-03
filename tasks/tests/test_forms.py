from django.test import TestCase
from tasks.forms import TaskCreateForm
from django.contrib.auth.models import User

from tasks.models import STATUS_CHOICES, Task

class TaskCreateFormTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="bruce_wayne", password="i_am_batman")

    def test_forms(self):
        form_data = {'title': 'something',
                    "description":"hello",
                    "user":self.user,
                    "priority":1,
                    "completed":False,
                    "status":STATUS_CHOICES[0][0]}
        form = TaskCreateForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_title_clean(self):
        form_data = {'title': 'task one',
                    "description":"hello",
                    "user":self.user,
                    "priority":10,
                    "completed":False,
                    "deleted":False,
                    "status":STATUS_CHOICES[0][0]}
        form = TaskCreateForm(data=form_data)
        form.save()
        self.assertEqual(Task.objects.get(pk=1).title,"TASK ONE")