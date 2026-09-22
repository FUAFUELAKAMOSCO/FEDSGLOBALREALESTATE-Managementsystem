from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    path('', views.booking_list, name='list'),
    path('today/', views.todays_bookings, name='today'),
    path('new/', views.booking_create, name='create'),
    path('<int:pk>/edit/', views.booking_edit, name='edit'),
    path('<int:pk>/status/<str:status>/', views.booking_status_update, name='status_update'),
    path('<int:pk>/delete/', views.booking_delete, name='delete'),
]