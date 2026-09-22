from django import forms
from django.contrib.auth import get_user_model
from .models import Contact

User = get_user_model()


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['full_name', 'phone', 'email', 'source', 'interest',
                  'budget', 'status', 'assigned_agent', 'notes']
        widgets = {
            'full_name': forms.TextInput(attrs={'placeholder': 'e.g. Sarah Mbida'}),
            'phone': forms.TextInput(attrs={'placeholder': 'e.g. +237 671 234 567'}),
            'email': forms.EmailInput(attrs={'placeholder': 'e.g. client@example.com'}),
            'budget': forms.NumberInput(attrs={'placeholder': 'Budget in CFA (e.g. 50000000)'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Specific preferences, property interests, or background notes...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['assigned_agent'].queryset = User.objects.filter(is_active=True).order_by('first_name', 'username')
        self.fields['assigned_agent'].empty_label = "Unassigned / General Pool"

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '').strip()
        if not phone:
            raise forms.ValidationError("A valid phone number is required to contact this client.")
        return phone