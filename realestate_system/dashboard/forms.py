import os
from django import forms
from django.core.exceptions import ValidationError
from .models import MediaUpload
from properties.models import Property


ALLOWED_EXTENSIONS = {
    'PHOTO': ['.png', '.jpg', '.jpeg', '.webp'],
    'VIDEO': ['.mp4', '.webm', '.mov', '.avi'],
    'PDF': ['.pdf'],
    'WORD': ['.doc', '.docx'],
}

ALL_ALLOWED_EXTS = [ext for exts in ALLOWED_EXTENSIONS.values() for ext in exts]


class MediaUploadForm(forms.ModelForm):
    file = forms.FileField(
        required=True,
        label="Select File",
        help_text="Supported formats: Videos (.mp4, .webm, .mov), Photos (.png, .jpg, .webp), Documents (.pdf, .doc, .docx).",
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'id': 'media-file-input',
            'accept': '.png,.jpg,.jpeg,.webp,.mp4,.webm,.mov,.avi,.pdf,.doc,.docx'
        })
    )

    class Meta:
        model = MediaUpload
        fields = ['title', 'file', 'related_property']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Registered Title Deed - Buea Plot 4B, or Drone Video Tour'
            }),
            'related_property': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['related_property'].queryset = Property.objects.all().order_by('-created_at')
        self.fields['related_property'].empty_label = "General Agency Vault (No specific property)"

    def clean_file(self):
        f = self.cleaned_data.get('file')
        if not f:
            raise ValidationError("Please select a file to upload.")

        ext = os.path.splitext(f.name)[1].lower()
        if ext not in ALL_ALLOWED_EXTS:
            raise ValidationError(
                f"Unsupported file format '{ext}'. Allowed files: PNG, JPG, WEBP, MP4, WEBM, MOV, PDF, DOC, DOCX."
            )

        # Max file size: 100MB for video, 25MB for others
        if ext in ALLOWED_EXTENSIONS['VIDEO'] and f.size > 100 * 1024 * 1024:
            raise ValidationError("Video files cannot exceed 100MB.")
        elif ext not in ALLOWED_EXTENSIONS['VIDEO'] and f.size > 25 * 1024 * 1024:
            raise ValidationError("Image and Document files cannot exceed 25MB.")

        return f
