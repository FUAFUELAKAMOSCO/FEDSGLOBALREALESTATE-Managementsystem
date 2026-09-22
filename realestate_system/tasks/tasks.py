import logging
from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

from .models import Task

logger = logging.getLogger(__name__)


@shared_task
def notify_task_owner(task_id):
    try:
        task = Task.objects.get(id=task_id)
    except Task.DoesNotExist:
        return f"Task {task_id} not found"

    if task.owner and task.owner.email:
        try:
            send_mail(
                f"New task assigned: {task.title}",
                f"Hello {task.owner.get_full_name() or task.owner.username},\n\n"
                f"You have been assigned a new task.\n\n"
                f"Title: {task.title}\n"
                f"Priority: {task.get_priority_display()}\n"
                f"Due Date: {task.due_date}\n"
                f"Description: {task.description or 'No description provided.'}\n\n"
                f"Regards,\nFred's Real Estate System",
                settings.DEFAULT_FROM_EMAIL,
                [task.owner.email],
                fail_silently=True,
            )
        except Exception as e:
            logger.warning(f"Could not send notification email for task {task_id}: {e}")
    return f"Owner notified for task {task_id}"


@shared_task
def send_morning_digest():
    from django.contrib.auth import get_user_model
    User = get_user_model()
    today = timezone.now().date()

    for user in User.objects.filter(is_active=True).exclude(email=''):
        own_tasks = Task.objects.filter(owner=user, status__in=['TODO', 'IN_PROGRESS'])
        today_tasks = own_tasks.filter(due_date=today)
        overdue = own_tasks.filter(due_date__lt=today)

        if not (today_tasks.exists() or overdue.exists()):
            continue

        lines = [f"Good morning {user.get_full_name() or user.username},\n"]
        if today_tasks.exists():
            lines.append("TODAY'S TASKS:")
            for t in today_tasks:
                lines.append(f"  • [{t.get_priority_display()}] {t.title}")
            lines.append("")
        if overdue.exists():
            lines.append("OVERDUE TASKS:")
            for t in overdue:
                lines.append(f"  ⚠ {t.title} (due {t.due_date})")

        try:
            send_mail(
                f"Daily digest - {today:%B %d, %Y}",
                "\n".join(lines),
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=True,
            )
        except Exception as e:
            logger.warning(f"Failed to send digest to {user.email}: {e}")
    return "Digest sent"


@shared_task
def send_overdue_alert():
    from django.contrib.auth import get_user_model
    User = get_user_model()
    today = timezone.now().date()

    overdue = Task.objects.filter(due_date__lt=today).exclude(status='DONE')
    by_owner = {}
    for t in overdue:
        by_owner.setdefault(t.owner, []).append(t)

    for owner, items in by_owner.items():
        if owner and owner.email:
            body = [f"Hello {owner.get_full_name() or owner.username},\n", "Overdue tasks:\n"]
            for t in items:
                body.append(f"  ⚠ {t.title} (due {t.due_date})")
            try:
                send_mail(
                    "Overdue tasks reminder",
                    "\n".join(body),
                    settings.DEFAULT_FROM_EMAIL,
                    [owner.email],
                    fail_silently=True,
                )
            except Exception as e:
                logger.warning(f"Failed to send overdue alert to {owner.email}: {e}")

    ceo = User.objects.filter(role='CEO', is_active=True).first()
    if ceo and ceo.email and overdue.exists():
        report = ["Overdue tasks company-wide:\n"]
        for owner, items in by_owner.items():
            report.append(f"\n{owner}:")
            for t in items:
                report.append(f"  ⚠ {t.title} (due {t.due_date})")
        try:
            send_mail(
                f"CEO Overdue Report - {today}",
                "\n".join(report),
                settings.DEFAULT_FROM_EMAIL,
                [ceo.email],
                fail_silently=True,
            )
        except Exception as e:
            logger.warning(f"Failed to send CEO overdue report: {e}")
    return f"Sent overdue alerts ({overdue.count()})"
