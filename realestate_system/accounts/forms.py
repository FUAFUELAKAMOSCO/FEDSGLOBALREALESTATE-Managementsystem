import os
from django import forms
from django.core.exceptions import ValidationError
from .models import User


class UserProfileUpdateForm(forms.ModelForm):
    avatar = forms.ImageField(
        required=False,
        label="Profile Photo / Avatar",
        help_text="Upload a photo (PNG, JPG, JPEG, WebP). Maximum size 5MB.",
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'})
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone', 'avatar']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'name@example.com'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+237 6XX XXX XXX'}),
        }

    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
        if avatar and hasattr(avatar, 'size'):
            # Check file size (5MB max)
            if avatar.size > 5 * 1024 * 1024:
                raise ValidationError("Profile image file size cannot exceed 5MB.")
            ext = os.path.splitext(avatar.name)[1].lower()
            if ext not in ['.jpg', '.jpeg', '.png', '.webp']:
                raise ValidationError("Allowed formats for profile photo are PNG, JPG, JPEG, or WebP.")
        return avatar


class UserDeleteConfirmForm(forms.Form):
    confirmation = forms.CharField(
        max_length=50,
        required=True,
        label="Type 'DELETE' to confirm",
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg border-danger text-center fw-bold',
            'placeholder': 'DELETE',
            'autocomplete': 'off'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password to authorize deletion'
        }),
        required=True,
        label="Your Account Password"
    )

    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_confirmation(self):
        val = self.cleaned_data.get('confirmation', '').strip()
        if val != 'DELETE':
            raise ValidationError("You must type exact uppercase 'DELETE' to confirm account deletion.")
        return val

    def clean_password(self):
        pwd = self.cleaned_data.get('password')
        if self.user and not self.user.check_password(pwd):
            raise ValidationError("Incorrect password entered. Account deletion cancelled for security.")
        return pwd
