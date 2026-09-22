from django.urls import path
from . import views

app_name = 'properties'

urlpatterns = [
    path('', views.landing_page, name='landing'),
    path('property/create/', views.property_create, name='create'),
    path('property/<slug:slug>/', views.property_detail, name='detail'),
    path('property/<slug:slug>/edit/', views.property_edit, name='edit'),
    path('property/<slug:slug>/inquire/', views.property_inquire, name='inquire'),
    path('property/<slug:slug>/book-visit/', views.property_book_visit, name='book_visit'),
    path('properties/', views.properties_catalog, name='catalog'),
]
