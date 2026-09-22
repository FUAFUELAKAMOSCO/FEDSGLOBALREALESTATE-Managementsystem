from django.contrib import admin
from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('client', 'property_address', 'booking_datetime', 'status', 'assigned_to')
    list_filter = ('status', 'booking_type')