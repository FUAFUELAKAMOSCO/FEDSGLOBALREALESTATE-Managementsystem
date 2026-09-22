import re
from django.db import models
from django.conf import settings
from django.urls import reverse


class Contact(models.Model):
    SOURCE_CHOICES = [
        ('WEBSITE', 'Website'), ('WHATSAPP', 'WhatsApp'), ('REFERRAL', 'Referral'),
        ('WALKIN', 'Walk-in'), ('CALL', 'Phone Call'),
    ]
    INTEREST_CHOICES = [
        ('BUY', 'Buy'), ('RENT', 'Rent'), ('SELL', 'Sell'), ('INVEST', 'Invest'),
    ]
    STATUS_CHOICES = [
        ('NEW', 'New'), ('CONTACTED', 'Contacted'), ('VIEWING', 'Viewing'),
        ('NEGOTIATING', 'Negotiating'), ('CLOSED', 'Closed'), ('LOST', 'Lost'),
    ]

    full_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=30)
    email = models.EmailField(blank=True)
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default='WEBSITE')
    interest = models.CharField(max_length=20, choices=INTEREST_CHOICES, default='BUY')
    budget = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='NEW')
    assigned_agent = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='assigned_contacts'
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_contact = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.full_name

    def get_absolute_url(self):
        return reverse('contacts:edit', kwargs={'pk': self.pk})

    @property
    def clean_phone_number(self):
        return re.sub(r'\D', '', self.phone or '')

    @property
    def whatsapp_url(self):
        cleaned = self.clean_phone_number
        return f"https://wa.me/{cleaned}" if cleaned else ""