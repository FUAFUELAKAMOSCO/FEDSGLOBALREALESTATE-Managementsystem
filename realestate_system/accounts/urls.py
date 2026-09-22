from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('profile/', views.profile_view, name='profile_view'),
    path('profile/edit/', views.profile_update, name='profile_edit'),
    path('profile/delete/', views.profile_delete, name='profile_delete'),
]
