import os
from django.db.models import Q


def company_info(request):
    base_data = {
        'COMPANY_NAME': os.getenv('COMPANY_NAME', "Fred's Global Real Estate"),
        'COMPANY_TAGLINE': os.getenv('COMPANY_TAGLINE', 'Verified Titled Lands & Luxury Living in Cameroon'),
        'COMPANY_PHONE': os.getenv('COMPANY_PHONE', '+237 679 798 244'),
        'COMPANY_WHATSAPP': os.getenv('COMPANY_WHATSAPP', '+237679798244'),
        'COMPANY_EMAIL': os.getenv('COMPANY_EMAIL', 'contact@fredsglobalrealestate.com'),
        'COMPANY_LOCATION': os.getenv('COMPANY_LOCATION', 'Mile 18 Junction Buea'),
        'unread_notifications_count': 0,
        'has_unread_messages': False,
        'recent_unread_notifications': [],
        'is_authorized_dashboard_user': False,
    }

    if hasattr(request, 'user') and request.user.is_authenticated:
        from .models import Notification
        from contacts.models import Contact

        # Check authorization
        is_auth = (
            request.user.is_active and
            getattr(request.user, 'active', True) and
            (
                request.user.is_superuser or
                request.user.is_staff or
                getattr(request.user, 'role', None) in [
                    'CEO', 'SECRETARIAT', 'FIELD_MANAGER', 'FINANCIAL', 'AGENT', 'ACCOUNTANT', 'ADMIN'
                ]
            )
        )
        base_data['is_authorized_dashboard_user'] = is_auth

        # Count unread notifications
        try:
            notif_qs = Notification.objects.filter(
                Q(recipient=request.user) | Q(recipient__isnull=True),
                is_read=False
            )
            unread_notifs_count = notif_qs.count()

            # Also consider new incoming contacts/leads as unread messages
            new_leads_count = Contact.objects.filter(status='NEW').count()
            total_active_messages = unread_notifs_count + new_leads_count

            base_data['unread_notifications_count'] = total_active_messages
            base_data['has_unread_messages'] = (total_active_messages > 0)

            # Build list of recent items for notification dropdown
            recent_items = list(notif_qs[:5])
            if new_leads_count > 0 and len(recent_items) < 5:
                recent_leads = Contact.objects.filter(status='NEW')[:3]
                for lead in recent_leads:
                    recent_items.append({
                        'title': f"New Lead: {lead.full_name}",
                        'message': f"Interested in {lead.get_interest_display()} ({lead.phone})",
                        'link': f"/contacts/{lead.id}/edit/",
                        'notification_type': 'INQUIRY',
                        'created_at': lead.created_at,
                        'is_synthetic': True,
                    })

            base_data['recent_unread_notifications'] = recent_items
        except Exception:
            # Handle during database migrations or cold start
            pass

    return base_data