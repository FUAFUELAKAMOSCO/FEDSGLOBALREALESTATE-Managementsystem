from django import forms
from .models import ActivityLog


class ActivityLogForm(forms.ModelForm):
    class Meta:
        model = ActivityLog
        fields = ['related_client', 'action', 'summary', 'outcome']
        widgets = {'summary': forms.Textarea(attrs={'rows': 3})}