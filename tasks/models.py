
from django.db import models

from django.contrib.auth.models import User


class Task(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    completed = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)
    user = models.ForeignKey(User , on_delete=models.CASCADE , null=True,blank=True)
    priority = models.IntegerField(default=-1)

    def pretty_date(self):
        return self.created_date.strftime("%a %d %b")

    def calculateComplete(self):
        return Task.objects.filter(deleted=False, completed=True,user=self.user).count()
    
    def calculateTotal(self):
        return Task.objects.filter(deleted=False,user=self.user).count()

    def __str__(self):
        return self.title