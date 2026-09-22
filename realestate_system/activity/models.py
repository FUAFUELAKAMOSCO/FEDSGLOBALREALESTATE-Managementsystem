from django.db import models
from django.conf import settings


class ActivityLog(models.Model):
    ACTION_CHOICES = [
        ('CALLED', 'Called'), ('EMAILED', 'Emailed'),
        ('MET', 'Met'), ('WHATSAPP', 'WhatsApp'), ('NOTE', 'Note'),
    ]

    person = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='activities')
    related_client = models.ForeignKey('contacts.Contact', on_delete=models.CASCADE,
                                       null=True, blank=True, related_name='activities')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    summary = models.TextField()
    outcome = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Activity Logs'

    def __str__(self):
        return f"{self.person} - {self.action} - {self.created_at:%Y-%m-%d %H:%M}"