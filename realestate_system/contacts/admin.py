from django.contrib import admin
from .models import Contact


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'phone', 'email', 'source', 'interest', 'status', 'assigned_agent', 'created_at')
    list_filter = ('status', 'source', 'interest', 'created_at')
    search_fields = ('full_name', 'phone', 'email', 'notes')
    list_select_related = ('assigned_agent',)
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)