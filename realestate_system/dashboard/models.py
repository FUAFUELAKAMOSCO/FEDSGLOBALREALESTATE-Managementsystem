from django.db import models
from django.conf import settings
import os


class BlockchainBlock(models.Model):
    ACTION_CHOICES = [
        ('GENESIS', 'Genesis Block'),
        ('PROPERTY_CREATE', 'Property Registration'),
        ('PROPERTY_UPDATE', 'Property Update'),
        ('TITLE_DEED_UPLOAD', 'Legal Title Deed Upload'),
        ('MEDIA_UPLOAD', 'Media & File Upload'),
        ('INQUIRY_RECEIVED', 'Client Inquiry / Lead Registered'),
        ('BOOKING_SCHEDULED', 'Site Visit / Booking Scheduled'),
        ('PROFILE_UPDATE', 'User Profile Update'),
        ('SECURITY_AUDIT', 'CIA Security Triad Verification'),
    ]

    index = models.PositiveIntegerField(unique=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    timestamp_str = models.CharField(max_length=50)
    action_type = models.CharField(max_length=60, choices=ACTION_CHOICES, default='SECURITY_AUDIT')
    record_id = models.CharField(max_length=100, blank=True)
    data_payload = models.JSONField(default=dict)
    data_hash = models.CharField(max_length=64)
    previous_hash = models.CharField(max_length=64)
    block_hash = models.CharField(max_length=64)
    nonce = models.IntegerField(default=0)
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['-index']
        verbose_name = 'Blockchain Block'
        verbose_name_plural = 'Blockchain Blocks'

    def __str__(self):
        return f"Block #{self.index} [{self.action_type}] - {self.block_hash[:12]}..."


class Notification(models.Model):
    TYPE_CHOICES = [
        ('INQUIRY', 'Client Inquiry / Message'),
        ('BOOKING', 'Booking Request'),
        ('TASK', 'Task Alert'),
        ('SECURITY', 'CIA Blockchain Alert'),
        ('SYSTEM', 'System Alert'),
    ]

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notifications',
        help_text="Leave empty to broadcast to all authorized staff/managers"
    )
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=30, choices=TYPE_CHOICES, default='INQUIRY')
    link = models.CharField(max_length=255, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.notification_type}] {self.title} ({'Read' if self.is_read else 'Unread'})"


class MediaUpload(models.Model):
    TYPE_CHOICES = [
        ('PHOTO', 'Photo / PNG / JPG Image'),
        ('VIDEO', 'Video (MP4 / WebM / MOV)'),
        ('PDF', 'PDF Document'),
        ('WORD', 'Word Document (.doc / .docx)'),
    ]

    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='media_vault/%Y/%m/')
    file_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='PHOTO')
    mime_type = models.CharField(max_length=100, blank=True)
    file_size = models.BigIntegerField(default=0)
    sha256_hash = models.CharField(max_length=64, blank=True, help_text="Cryptographic SHA-256 fingerprint for CIA Integrity")
    related_property = models.ForeignKey(
        'properties.Property',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='media_uploads'
    )
    blockchain_block = models.ForeignKey(
        BlockchainBlock,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='associated_media'
    )
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.get_file_type_display()})"

    @property
    def file_extension(self):
        name = self.file.name if self.file else ''
        return os.path.splitext(name)[1].lower()

    @property
    def formatted_size(self):
        size = self.file_size
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size / 1024:.1f} KB"
        else:
            return f"{size / (1024 * 1024):.2f} MB"
