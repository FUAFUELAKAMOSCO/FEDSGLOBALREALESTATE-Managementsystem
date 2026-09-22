from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils.text import slugify


class Property(models.Model):
    TYPE_CHOICES = [
        ('LAND', 'Land / Plots'),
        ('RESIDENTIAL', 'Residential House'),
        ('VILLA', 'Luxury Villa'),
        ('COMMERCIAL', 'Commercial Property'),
        ('APARTMENT', 'Apartment'),
    ]

    STATUS_CHOICES = [
        ('AVAILABLE', 'Available / Active'),
        ('UNDER_OFFER', 'Under Offer'),
        ('RESERVED', 'Reserved'),
        ('SOLD', 'Sold Out'),
    ]

    title = models.CharField(max_length=255, default="Prime Property Located Behind Cathedral around Blue Empire")
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    subtitle = models.CharField(
        max_length=350,
        blank=True,
        default="We are launching the prime property located behind Cathedral around Blue Empire in Buea, Cameroon."
    )
    property_type = models.CharField(max_length=30, choices=TYPE_CHOICES, default='LAND')
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='AVAILABLE')
    
    price = models.DecimalField(max_digits=14, decimal_places=2, default=2000000.00)
    currency = models.CharField(max_length=15, default='FCFA')
    price_prefix = models.CharField(max_length=50, blank=True, default="From")
    price_suffix = models.CharField(max_length=50, blank=True, default="per 400 m² plot")

    area_sqm = models.DecimalField(max_digits=10, decimal_places=2, default=400.00)
    area_display = models.CharField(max_length=100, default='400 m² (Acres and Hectares available)')
    topography = models.CharField(max_length=100, default='Level / 100% Flat')

    location = models.CharField(max_length=255, default='Behind Cathedral around Blue Empire, Buea, Cameroon')
    city = models.CharField(max_length=100, default='Buea')
    region = models.CharField(max_length=100, default='South West Region')
    country = models.CharField(max_length=100, default='Cameroon')

    description = models.TextField(
        default=(
            "We are proudly launching the prime property located behind Cathedral around Blue Empire in Buea, Cameroon. "
            "Strategically situated in Buea's fastest booming residential corridor, this property offers pristine, 100% "
            "level topography, direct motorable access, surveyed plot boundaries with permanent boundary pillars, "
            "and scenic vistas of Mount Cameroon. Guaranteed by Fred's Global Real Estate."
        )
    )

    documents = models.JSONField(
        default=list,
        help_text="List of official legal documents (e.g. Chief Attestation, Site Plan, Transfer of ownership, Deed)"
    )
    landmarks = models.JSONField(
        default=list,
        help_text="Key landmarks with drive times and descriptions"
    )
    features = models.JSONField(
        default=list,
        help_text="Key highlights, e.g. Level topography, electricity corridor, road access"
    )

    featured_image = models.CharField(max_length=255, default='images/hero.jpg')
    gallery_images = models.JSONField(default=list, blank=True)
    video_url = models.URLField(blank=True, help_text="YouTube or Vimeo tour link")

    is_featured = models.BooleanField(default=True)
    views_count = models.PositiveIntegerField(default=0)

    assigned_agent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_properties'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Property'
        verbose_name_plural = 'Properties'
        ordering = ['-is_featured', '-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title) or 'property'
            slug = base_slug
            counter = 1
            while Property.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.location})"

    def get_absolute_url(self):
        return reverse('properties:detail', kwargs={'slug': self.slug})

    @property
    def formatted_price(self):
        return f"{int(self.price):,} {self.currency}".replace(',', ' ')

    @property
    def image_url(self):
        if not self.featured_image:
            from django.templatetags.static import static
            return static('images/hero.jpg')
        if self.featured_image.startswith(('http://', 'https://')):
            return self.featured_image
        if self.featured_image.startswith('/media/'):
            return self.featured_image
        if self.featured_image.startswith('media/'):
            return f"/{self.featured_image}"
        if self.featured_image.startswith('/static/'):
            return self.featured_image
        from django.templatetags.static import static
        return static(self.featured_image)
