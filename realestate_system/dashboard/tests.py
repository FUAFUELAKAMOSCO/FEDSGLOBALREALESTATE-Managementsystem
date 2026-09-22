from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from contacts.models import Contact
from bookings.models import Booking
from tasks.models import Task
from activity.models import ActivityLog

User = get_user_model()


class DashboardViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.agent = User.objects.create_user(
            username='dashboardagent',
            email='agent@example.com',
            password='Password123!',
            role='AGENT'
        )
        self.ceo = User.objects.create_user(
            username='dashboardceo',
            email='ceo@example.com',
            password='Password123!',
            role='CEO',
            is_staff=True
        )
        self.contact = Contact.objects.create(
            full_name='Diane Mbarga',
            phone='+237 677 88 99 00',
            email='diane@example.com',
            status='NEW',
            assigned_agent=self.agent
        )
        self.booking = Booking.objects.create(
            client=self.contact,
            property_address='Boulevard de la Liberte, Akwa, Douala',
            booking_datetime=timezone.now(),
            booking_type='VIEWING',
            status='CONFIRMED',
            assigned_to=self.agent
        )
        self.task = Task.objects.create(
            title='Follow up on Akwa showing',
            owner=self.agent,
            related_client=self.contact,
            priority='HIGH',
            due_date=timezone.now().date(),
            status='TODO'
        )
        self.activity = ActivityLog.objects.create(
            person=self.agent,
            related_client=self.contact,
            action='CALLED',
            summary='Discussed budget and scheduling',
            outcome='Agreed to Akwa visit'
        )

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse('dashboard:home'))
        self.assertEqual(response.status_code, 302)

    def test_dashboard_renders_for_agent(self):
        self.client.force_login(self.agent)
        response = self.client.get(reverse('dashboard:home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/home.html')
        self.assertContains(response, 'Diane Mbarga')
        self.assertContains(response, 'Follow up on Akwa showing')
        self.assertContains(response, 'Executive Real Estate Dashboard')
        self.assertEqual(response.context['total_contacts'], 1)
        self.assertEqual(response.context['total_bookings_today'], 1)

    def test_dashboard_renders_for_ceo(self):
        self.client.force_login(self.ceo)
        response = self.client.get(reverse('dashboard:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Diane Mbarga')

    def test_context_processor_company_info(self):
        self.client.force_login(self.agent)
        response = self.client.get(reverse('dashboard:home'))
        self.assertIn('COMPANY_NAME', response.context)
        self.assertIn('COMPANY_TAGLINE', response.context)
