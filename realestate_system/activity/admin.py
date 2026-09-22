from django.contrib import admin
from .models import ActivityLog


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('person', 'related_client', 'action', 'created_at')
    list_filter = ('action',)