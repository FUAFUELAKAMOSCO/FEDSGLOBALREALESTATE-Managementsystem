from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta

from .models import Contact
from tasks.models import Task


@receiver(pre_save, sender=Contact)
def detect_status_change(sender, instance, **kwargs):
    if not instance.pk:
        instance._old_status = None
        return
    old_status = Contact.objects.filter(pk=instance.pk).values_list('status', flat=True).first()
    instance._old_status = old_status


@receiver(post_save, sender=Contact)
def create_task_on_status_change(sender, instance, created, **kwargs):
    if created or not hasattr(instance, '_old_status'):
        return
    if instance._old_status == instance.status or not instance.assigned_agent:
        return

    mapping = {
        'VIEWING': ('Schedule viewing', 'HIGH', 2),
        'NEGOTIATING': ('Follow up negotiation', 'HIGH', 1),
        'CLOSED': ('Send thank-you + request referral', 'MEDIUM', 3),
        'LOST': ('Log reason for loss', 'LOW', 1),
    }
    if instance.status in mapping:
        title, priority, days = mapping[instance.status]
        Task.objects.create(
            title=f"{title} for {instance.full_name}",
            owner=instance.assigned_agent,
            related_client=instance,
            priority=priority,
            due_date=timezone.now().date() + timedelta(days=days),
        )