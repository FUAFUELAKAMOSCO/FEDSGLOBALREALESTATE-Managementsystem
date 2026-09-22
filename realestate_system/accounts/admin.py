from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'active')
    list_filter = ('role', 'active')
    fieldsets = UserAdmin.fieldsets + (
        ('Real Estate Role', {'fields': ('role', 'phone', 'active')}),
    )