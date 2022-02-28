import time
from datetime import datetime, timedelta
from celery.task import periodic_task
from django.core.mail import send_mail
from django.utils import timezone
from task_manager.celery import app
from django.db.models import Count
from tasks.models import ReportSchedule, Task


@periodic_task(run_every=timedelta(seconds=60))
def send_scheduled_emails():
    print("send scheduled emails")
    update_qs = []
    dt = datetime.now()
    # filter all reports which have to be sent at times less than equal to now and
    # exclude those which have been processed today,
    # hence the reports missed in 24hr will be reprocessed
    reports = ReportSchedule.objects.filter(report_at__lte=dt).exclude(last_run_at__day=dt.day)
    for report in reports:
        print(report)
        pending_tasks = Task.objects.filter(user=report.user,completed=False,deleted=False).values('status').annotate(total=Count('status')).order_by('total')
        email_content = f"Hey {report.user}, here is your daily report:\n"
        for status in pending_tasks:
            email_content += f"Task {status['status']} : {status['total']}\n"
        if report.email:
            send_mail("Pending tasks from Tasks Manager",email_content,"eg@eg.com",{report.email})
        print(f"Email sent to {report.user.id}")
        report.last_run_at = timezone.now()
        # report.next_run_at = report.report_at + timedelta(days=1)
        update_qs.append(report)
    # bulkupdate does not call save() hence last_modified feature of model can't be used.
    updated_qs = ReportSchedule.objects.bulk_update(update_qs,['last_run_at'])

@app.task
def bg_jobs():
    print("this is running in bg")
    for i in range(10):
        time.sleep(1)
        print(i)
