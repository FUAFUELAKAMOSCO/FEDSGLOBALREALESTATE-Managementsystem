from django import forms
from .models import Booking


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['client', 'property_address', 'booking_datetime',
                  'booking_type', 'assigned_to', 'notes']
        widgets = {
            'booking_datetime': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }