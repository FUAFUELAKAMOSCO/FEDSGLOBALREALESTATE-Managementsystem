from django import forms
from django.utils import timezone


COUNTRY_CODE_CHOICES = [
    ('+237', 'Cameroon (+237)'),
    ('+1', 'USA / Canada (+1)'),
    ('+44', 'UK (+44)'),
    ('+33', 'France (+33)'),
    ('+49', 'Germany (+49)'),
    ('+32', 'Belgium (+32)'),
    ('+39', 'Italy (+39)'),
    ('+27', 'South Africa (+27)'),
    ('+234', 'Nigeria (+234)'),
    ('+971', 'UAE (+971)'),
    ('OTHER', 'Other Country'),
]


class InquiryForm(forms.Form):
    full_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your Full Name *',
            'required': True,
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your Email Address *',
            'required': True,
        })
    )
    country_code = forms.ChoiceField(
        choices=COUNTRY_CODE_CHOICES,
        initial='+237',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    phone = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Phone / WhatsApp Number *',
            'required': True,
        })
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'I am interested in acquiring a plot behind Cathedral around Blue Empire, Buea. Please send me full pricing, documentation and site visit details.',
            'required': True,
        })
    )


class ScheduleVisitForm(forms.Form):
    full_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your Full Name *',
            'required': True,
        })
    )
    phone = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Phone / WhatsApp Number *',
            'required': True,
        })
    )
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email Address (optional)',
        })
    )
    visit_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'required': True,
        })
    )
    visit_time = forms.TimeField(
        widget=forms.TimeInput(attrs={
            'class': 'form-control',
            'type': 'time',
            'value': '10:00',
            'required': True,
        })
    )
    visit_type = forms.ChoiceField(
        choices=[
            ('SITE_VISIT', 'On-Site Guided Inspection (Buea shuttle available)'),
            ('MEETING', 'Agency Office Consultation'),
            ('CALL', 'WhatsApp Video Tour / Virtual Walkthrough'),
        ],
        initial='SITE_VISIT',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': 'Special requests, number of attendees, or questions...',
        })
    )


from django.contrib.auth import get_user_model
from django.core.files.storage import default_storage
from django.utils.text import slugify
from .models import Property

User = get_user_model()


class PropertyForm(forms.ModelForm):
    featured_image_file = forms.ImageField(
        required=False,
        label="Upload Featured Photo",
        help_text="Upload a photo from your computer (JPG, PNG, WebP).",
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'})
    )
    featured_image_preset = forms.ChoiceField(
        required=False,
        label="Or Choose Preset Image",
        choices=[
            ('', '-- None / Use Uploaded Photo or Default --'),
            ('images/hero.jpg', 'Hero Estate Aerial View (hero.jpg)'),
            ('images/plots.jpg', 'Demarcated Plots & Survey Pillars (plots.jpg)'),
            ('images/plan.jpg', 'Approved Cadastral Master Plan (plan.jpg)'),
            ('images/villas.jpg', 'Modern Executive Villa Architecture (villas.jpg)'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    featured_image_custom_url = forms.CharField(
        required=False,
        label="Or Photo URL",
        help_text="External image link or static path.",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'https://... or images/...'})
    )
    documents_input = forms.CharField(
        required=False,
        label="Official Legal Documents",
        help_text="Enter documents, one per line. Format: Document Name: Short description",
        widget=forms.Textarea(attrs={
            'class': 'form-control font-monospace',
            'rows': 4,
            'placeholder': "Chief Attestation: Official customary council endorsement and royal blessing\nCadastral Site Plan: Approved demarcation survey with official cadastral stamps\nTransfer of Ownership: Deed of assignment executed by certified notary\nRegistered Title Deed: Litigation-free, unencumbered land ownership tenure"
        })
    )
    features_input = forms.CharField(
        required=False,
        label="Key Highlights & Features",
        help_text="Enter key property features, one item per line.",
        widget=forms.Textarea(attrs={
            'class': 'form-control font-monospace',
            'rows': 5,
            'placeholder': "100% Flat & Level Topography - Zero excavation required\nPrime location in Buea high-growth corridor\nSurveyed perimeter with permanent boundary pillars\nImmediate building readiness for villas or duplexes\nDirect graded motorable road access connecting to arterial roads"
        })
    )
    landmarks_input = forms.CharField(
        required=False,
        label="Neighborhood Landmarks & Proximity",
        help_text="Enter landmarks, one per line. Format: Landmark Name | Travel Time | Description",
        widget=forms.Textarea(attrs={
            'class': 'form-control font-monospace',
            'rows': 4,
            'placeholder': "Mile 18 Junction Buea | 2 minute drive | Direct road connectivity & transport hub\nRegina Pacis Cathedral | 3 minute walk | Historic neighborhood landmark\nBuea Town Commercial Center | 5 minute drive | Banking sector, markets, and regional offices\nUniversity of Buea & Mile 17 | 10 minute drive | Major academic campus and regional transport terminal"
        })
    )

    class Meta:
        model = Property
        fields = [
            'title', 'subtitle', 'property_type', 'status', 'is_featured',
            'price', 'currency', 'price_prefix', 'price_suffix',
            'area_sqm', 'area_display', 'topography',
            'location', 'city', 'region', 'country',
            'description', 'video_url', 'assigned_agent'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 400 m² Prime Residential Plots at Mile 18 Junction'}),
            'subtitle': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Short engaging summary or tagline for the estate'}),
            'property_type': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '2000000'}),
            'currency': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'FCFA'}),
            'price_prefix': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Starting from'}),
            'price_suffix': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'per 400 m² titled plot'}),
            'area_sqm': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '400.00'}),
            'area_display': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '400 m² (Acres and Hectares available)'}),
            'topography': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '100% Level / Flat Topography'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Mile 18 Junction, Buea, South West Region, Cameroon'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Buea'}),
            'region': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'South West Region'}),
            'country': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Cameroon'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Provide a detailed, compelling description of the property, its location advantages, building readiness, tenure security, and investment potential...'
            }),
            'video_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://www.youtube.com/watch?v=...'}),
            'assigned_agent': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['assigned_agent'].queryset = User.objects.filter(is_active=True).order_by('first_name', 'username')
        self.fields['assigned_agent'].empty_label = "Unassigned (Company Pool)"

        if self.instance and self.instance.pk:
            # Pre-fill helper text fields from JSON
            if self.instance.documents and isinstance(self.instance.documents, list):
                doc_lines = []
                for d in self.instance.documents:
                    if isinstance(d, dict):
                        doc_lines.append(f"{d.get('name', '')}: {d.get('desc', '')}")
                    elif isinstance(d, str):
                        doc_lines.append(d)
                self.fields['documents_input'].initial = "\n".join(doc_lines)

            if self.instance.features and isinstance(self.instance.features, list):
                self.fields['features_input'].initial = "\n".join([str(f) for f in self.instance.features])

            if self.instance.landmarks and isinstance(self.instance.landmarks, list):
                lm_lines = []
                for lm in self.instance.landmarks:
                    if isinstance(lm, dict):
                        lm_lines.append(f"{lm.get('name', '')} | {lm.get('time', '')} | {lm.get('desc', '')}")
                    elif isinstance(lm, str):
                        lm_lines.append(lm)
                self.fields['landmarks_input'].initial = "\n".join(lm_lines)

            if self.instance.featured_image:
                if self.instance.featured_image in ['images/hero.jpg', 'images/plots.jpg', 'images/plan.jpg', 'images/villas.jpg']:
                    self.fields['featured_image_preset'].initial = self.instance.featured_image
                else:
                    self.fields['featured_image_custom_url'].initial = self.instance.featured_image

    def save(self, commit=True):
        instance = super().save(commit=False)

        # Handle Image
        uploaded_file = self.cleaned_data.get('featured_image_file')
        preset_img = self.cleaned_data.get('featured_image_preset')
        custom_url = self.cleaned_data.get('featured_image_custom_url', '').strip()

        if uploaded_file:
            import os
            import time
            ext = os.path.splitext(uploaded_file.name)[1].lower() or '.jpg'
            clean_slug = slugify(self.cleaned_data.get('title', 'property')[:25]) or 'prop'
            filename = f"property_{int(time.time())}_{clean_slug}{ext}"
            saved_path = default_storage.save(f"properties/{filename}", uploaded_file)
            instance.featured_image = f"media/{saved_path}".replace('\\', '/')
        elif preset_img:
            instance.featured_image = preset_img
        elif custom_url:
            instance.featured_image = custom_url
        elif not instance.featured_image:
            instance.featured_image = 'images/hero.jpg'

        # Parse Documents input
        doc_raw = self.cleaned_data.get('documents_input', '')
        if doc_raw.strip():
            docs = []
            for line in doc_raw.splitlines():
                line = line.strip()
                if not line:
                    continue
                if ':' in line:
                    n, d = line.split(':', 1)
                    docs.append({'name': n.strip(), 'desc': d.strip()})
                else:
                    docs.append({'name': line, 'desc': 'Verified legal document'})
            instance.documents = docs
        elif not instance.documents:
            instance.documents = [
                {'name': 'Chief Attestation', 'desc': 'Official customary council endorsement and royal blessing'},
                {'name': 'Cadastral Site Plan', 'desc': 'Approved demarcation survey with official cadastral stamps'},
                {'name': 'Transfer of Ownership', 'desc': 'Deed of assignment executed by certified notary'},
                {'name': 'Registered Title Deed', 'desc': 'Litigation-free, unencumbered land ownership tenure'},
            ]

        # Parse Features input
        feat_raw = self.cleaned_data.get('features_input', '')
        if feat_raw.strip():
            feats = [f.strip() for f in feat_raw.splitlines() if f.strip()]
            instance.features = feats
        elif not instance.features:
            instance.features = [
                '100% Flat & Level Topography - Zero excavation required',
                f"Prime location in {instance.city or 'Buea'}, Cameroon",
                'Surveyed perimeter with concrete boundary pillars',
                f"Spacious {instance.area_display or '400 m²'} plots",
                'Direct graded motorable road access',
                'Clean, dispute-free documentation guaranteed by notary'
            ]

        # Parse Landmarks input
        lm_raw = self.cleaned_data.get('landmarks_input', '')
        if lm_raw.strip():
            landmarks = []
            for line in lm_raw.splitlines():
                line = line.strip()
                if not line:
                    continue
                parts = [p.strip() for p in line.split('|')]
                name = parts[0]
                time_val = parts[1] if len(parts) > 1 else 'Nearby'
                desc = parts[2] if len(parts) > 2 else 'Local community point of interest'
                landmarks.append({
                    'name': name,
                    'time': time_val,
                    'icon': 'bi-geo-alt-fill',
                    'desc': desc
                })
            instance.landmarks = landmarks
        elif not instance.landmarks:
            instance.landmarks = [
                {'name': 'Mile 18 Junction Buea', 'time': '2 minute drive', 'icon': 'bi-signpost-2-fill', 'desc': 'Direct paved road connectivity and neighborhood hub'},
                {'name': 'Buea Town Commercial Center', 'time': '5 minute drive', 'icon': 'bi-shop-window', 'desc': 'Banking sector, markets, and administrative offices'},
                {'name': 'University of Buea & Mile 17', 'time': '10 minute drive', 'icon': 'bi-mortarboard-fill', 'desc': 'UB campus and central motor park'},
            ]

        if commit:
            instance.save()
        return instance

