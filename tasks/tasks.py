import time
from datetime import datetime, timedelta

from celery.schedules import crontab
from celery.task import periodic_task
from django.core.mail import send_mail
from task_manager.celery import app
from django.db.models import Count
from tasks.models import ReportSchedule, Task


@periodic_task(run_every=timedelta(seconds=60))
def send_scheduled_emails():
    reports = ReportSchedule.objects.all()
    for report in reports:
        if report.email:
            pending_tasks = Task.objects.filter(user=report.user,completed=False,deleted=False).values('status').annotate(total=Count('status')).order_by('total')
            email_content = f"Hey {report.user}, here is your daily report:\n"
            for status in pending_tasks:
                email_content += f"Task {status['status']} : {status['total']}\n"
            check_time = str(report.report_at)[:-3]==str(datetime.now().strftime("%H:%M"))
            if check_time:
                send_mail("Pending tasks from Tasks Manager",email_content,"eg@eg.com",{report.email})
                print(f"Email sent to {report.user.id}")

@app.task
def bg_jobs():
    print("this is running in bg")
    for i in range(10):
        time.sleep(1)
        print(i)
