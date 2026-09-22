from django.db import models
from django.conf import settings


class Booking(models.Model):
    TYPE_CHOICES = [
        ('VIEWING', 'Viewing'), ('CALL', 'Call'),
        ('MEETING', 'Meeting'), ('SITE_VISIT', 'Site Visit'),
    ]
    STATUS_CHOICES = [
        ('REQUESTED', 'Requested'), ('CONFIRMED', 'Confirmed'),
        ('COMPLETED', 'Completed'), ('NOSHOW', 'No-Show'),
        ('CANCELLED', 'Cancelled'),
    ]

    client = models.ForeignKey('contacts.Contact', on_delete=models.CASCADE, related_name='bookings')
    property_address = models.CharField(max_length=300)
    booking_datetime = models.DateTimeField()
    booking_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='VIEWING')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='REQUESTED')
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='assigned_bookings'
    )
    reminder_sent = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['booking_datetime']

    def __str__(self):
        return f"{self.client} @ {self.property_address} on {self.booking_datetime:%Y-%m-%d %H:%M}"