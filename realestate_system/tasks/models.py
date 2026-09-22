from django.db import models
from django.conf import settings
from django.utils import timezone


class Task(models.Model):
    PRIORITY_CHOICES = [
        ('LOW', 'Low'), ('MEDIUM', 'Medium'), ('HIGH', 'High'), ('URGENT', 'Urgent'),
    ]
    STATUS_CHOICES = [
        ('TODO', 'To Do'), ('IN_PROGRESS', 'In Progress'),
        ('BLOCKED', 'Blocked'), ('DONE', 'Done'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='owned_tasks')
    related_client = models.ForeignKey('contacts.Contact', on_delete=models.SET_NULL,
                                       null=True, blank=True, related_name='tasks')
    related_booking = models.ForeignKey('bookings.Booking', on_delete=models.SET_NULL,
                                        null=True, blank=True, related_name='tasks')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='MEDIUM')
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='TODO')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                   null=True, blank=True, related_name='created_tasks')
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['due_date', '-priority']

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"

    @property
    def is_overdue(self):
        return self.status != 'DONE' and self.due_date < timezone.now().date()