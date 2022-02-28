
from django.contrib.auth.models import User
from django.db import models
from datetime import datetime, timedelta
from django.utils import timezone
STATUS_CHOICES = (
    ("PENDING", "PENDING"),
    ("IN_PROGRESS", "IN_PROGRESS"),
    ("COMPLETED", "COMPLETED"),
    ("CANCELLED", "CANCELLED"),
)


class History(models.Model):
    task = models.ForeignKey("Task", on_delete=models.CASCADE)
    old_status =  models.CharField(max_length=100, choices=STATUS_CHOICES, default=STATUS_CHOICES[0][0])
    new_status =  models.CharField(max_length=100, choices=STATUS_CHOICES, default=STATUS_CHOICES[0][0])
    updated_at =  models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.updated_at.strftime("%a %d %b")
 
class Task(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    completed = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True)
    deleted = models.BooleanField(default=False)
    user = models.ForeignKey(User , on_delete=models.CASCADE , null=True,blank=True)
    priority = models.IntegerField(default=0)
    status = models.CharField(max_length=100, choices=STATUS_CHOICES, default=STATUS_CHOICES[0][0])

    def get_history(self):
        return History.objects.filter(task=self)

    def save(self, *args, **kwargs):
        super().save( *args, **kwargs)
        history = self.get_history()
        if history.exists():
            old_status = History.objects.filter(task=self).order_by('-updated_at').first().new_status
            if old_status != self.status:
                History.objects.create(task=self, old_status=old_status, new_status=self.status)
        else:
            History.objects.create(task=self, old_status='', new_status=self.status)

    def pretty_date(self):
        return self.created_date.strftime("%a %d %b")

    def calculateComplete(self):
        return Task.objects.filter(deleted=False, completed=True,user=self.user).count()
    
    def calculateTotal(self):
        return Task.objects.filter(deleted=False,user=self.user).count()

    def __str__(self):
        return self.title

def default_start_time():
    # now = datetime.now()
    now = timezone.now()
    start = now.replace(hour=20, minute=0, second=0, microsecond=0)
    return start

def default_last_runtime():
    # now = datetime.now() - timedelta(days=1)
    now = default_start_time()
    now -= timedelta(days=1)
    return now 

class ReportSchedule(models.Model):
    user = models.OneToOneField(User , on_delete=models.CASCADE, null=True,blank=True)
    report_at = models.TimeField(default=default_start_time)
    last_run_at = models.DateTimeField(default=default_last_runtime)
    # next_run_at = models.DateTimeField(default=default_start_time)
    email = models.EmailField(max_length=254)

    def __str__(self) :
        return f"{self.user} at {self.report_at} to {self.email}"
