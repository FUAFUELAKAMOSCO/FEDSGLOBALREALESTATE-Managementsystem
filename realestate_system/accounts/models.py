from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = [
        ('CEO', 'CEO / Manager'),
        ('SECRETARIAT', 'Secretariat'),
        ('FIELD_MANAGER', 'Field Work Manager'),
        ('FINANCIAL', 'Financial Manager'),
        ('AGENT', 'Agent'),
        ('ACCOUNTANT', 'Accountant'),
        ('ADMIN', 'Admin'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='AGENT')
    phone = models.CharField(max_length=30, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"

    @property
    def avatar_url(self):
        if self.avatar and hasattr(self.avatar, 'url'):
            return self.avatar.url
        return None

    @property
    def initials(self):
        first = (self.first_name or self.username or '?')[:1].upper()
        last = (self.last_name or '')[:1].upper()
        return f"{first}{last}" if last else first

    def is_authorized_staff(self):
        """Check if user has valid authorized access to the executive dashboard."""
        if not (self.is_active and self.active):
            return False
        if self.is_superuser or self.is_staff:
            return True
        return self.role in ['CEO', 'SECRETARIAT', 'FIELD_MANAGER', 'FINANCIAL', 'AGENT', 'ACCOUNTANT', 'ADMIN']