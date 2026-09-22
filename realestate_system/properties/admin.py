from django.contrib import admin
from .models import Property


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('title', 'location', 'price', 'area_sqm', 'property_type', 'status', 'is_featured', 'views_count')
    list_filter = ('property_type', 'status', 'is_featured', 'city')
    search_fields = ('title', 'location', 'description')
    prepopulated_fields = {'slug': ('title',)}
