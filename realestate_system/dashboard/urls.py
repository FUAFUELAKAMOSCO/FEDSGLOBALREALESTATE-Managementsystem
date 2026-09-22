from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('dashboard/', views.home, name='home'),
    path('dashboard/security/', views.blockchain_security_view, name='security'),
    path('dashboard/security/verify-api/', views.verify_chain_api, name='verify_chain_api'),
    path('dashboard/security/verify-file/', views.verify_document_hash_api, name='verify_document_hash_api'),
    path('dashboard/documents/', views.media_vault_view, name='media_vault'),
    path('dashboard/documents/<int:pk>/delete/', views.media_delete_view, name='media_delete'),
    path('dashboard/notifications/', views.notifications_list, name='notifications'),
    path('dashboard/notifications/<int:pk>/read/', views.mark_notification_read, name='mark_notification_read'),
    path('dashboard/notifications/mark-all-read/', views.mark_all_notifications_read, name='mark_all_read'),
]