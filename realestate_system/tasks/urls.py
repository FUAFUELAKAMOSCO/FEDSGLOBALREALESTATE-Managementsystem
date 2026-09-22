from django.urls import path
from . import views

app_name = 'tasks'

urlpatterns = [
    path('', views.task_list, name='list'),
    path('my/', views.my_tasks, name='my_tasks'),
    path('today/', views.today_tasks, name='today'),
    path('overdue/', views.overdue_tasks, name='overdue'),
    path('new/', views.task_create, name='create'),
    path('<int:pk>/edit/', views.task_edit, name='edit'),
    path('<int:pk>/toggle/', views.task_toggle, name='toggle'),
    path('<int:pk>/delete/', views.task_delete, name='delete'),
]