from datetime import timedelta
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from accounts.models import User
from contacts.models import Contact
from bookings.models import Booking


class BookingModelTest(TestCase):
    def setUp(self):
        self.client_user = User.objects.create_user(
            username='agent1', email='agent1@example.com', password='password123', role='AGENT'
        )
        self.contact = Contact.objects.create(
            full_name='Alice Smith', email='alice@example.com', phone='+237671112233', assigned_agent=self.client_user
        )
        self.booking = Booking.objects.create(
            client=self.contact,
            property_address='Plot 14, Behind Cathedral, Blue Empire',
            booking_datetime=timezone.now() + timedelta(days=2),
            booking_type='VIEWING',
            status='REQUESTED',
            assigned_to=self.client_user
        )

    def test_booking_str(self):
        self.assertIn('Alice Smith', str(self.booking))
        self.assertIn('Plot 14, Behind Cathedral, Blue Empire', str(self.booking))

    def test_booking_defaults(self):
        self.assertEqual(self.booking.status, 'REQUESTED')
        self.assertEqual(self.booking.booking_type, 'VIEWING')
        self.assertFalse(self.booking.reminder_sent)


class BookingViewsTest(TestCase):
    def setUp(self):
        self.agent = User.objects.create_user(
            username='agent_john', email='john@example.com', password='password123', role='AGENT'
        )
        self.ceo = User.objects.create_user(
            username='ceo_fred', email='fred@example.com', password='password123', role='CEO'
        )
        self.contact = Contact.objects.create(
            full_name='Marie Claire', email='marie@example.com', phone='+237672223344', assigned_agent=self.agent
        )
        self.booking = Booking.objects.create(
            client=self.contact,
            property_address='Wonya Mokomba, Buea',
            booking_datetime=timezone.now() + timedelta(days=1),
            booking_type='SITE_VISIT',
            status='CONFIRMED',
            assigned_to=self.agent
        )
        self.http_client = Client()

    def test_booking_list_requires_login(self):
        response = self.http_client.get(reverse('bookings:list'))
        self.assertEqual(response.status_code, 302)

    def test_booking_list_authenticated(self):
        self.http_client.login(username='agent_john', password='password123')
        response = self.http_client.get(reverse('bookings:list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Wonya Mokomba, Buea')
        self.assertIn('total_bookings', response.context)
        self.assertIn('type_labels_json', response.context)

    def test_booking_create_get(self):
        self.http_client.login(username='agent_john', password='password123')
        response = self.http_client.get(reverse('bookings:create'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)

    def test_booking_create_post(self):
        self.http_client.login(username='agent_john', password='password123')
        data = {
            'client': self.contact.id,
            'property_address': 'Plot 22, Limbe Seaside',
            'booking_datetime': (timezone.now() + timedelta(days=3)).strftime('%Y-%m-%dT%H:%M'),
            'booking_type': 'VIEWING',
            'assigned_to': self.agent.id,
            'notes': 'High priority customer looking for beachfront property.',
        }
        response = self.http_client.post(reverse('bookings:create'), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Booking.objects.filter(property_address='Plot 22, Limbe Seaside').exists())

    def test_booking_edit(self):
        self.http_client.login(username='agent_john', password='password123')
        data = {
            'client': self.contact.id,
            'property_address': 'Updated Wonya Mokomba Address',
            'booking_datetime': self.booking.booking_datetime.strftime('%Y-%m-%dT%H:%M'),
            'booking_type': 'MEETING',
            'assigned_to': self.agent.id,
            'notes': 'Updated meeting notes',
        }
        response = self.http_client.post(reverse('bookings:edit', args=[self.booking.id]), data)
        self.assertEqual(response.status_code, 302)
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.property_address, 'Updated Wonya Mokomba Address')
        self.assertEqual(self.booking.booking_type, 'MEETING')

    def test_booking_status_update(self):
        self.http_client.login(username='agent_john', password='password123')
        response = self.http_client.get(reverse('bookings:status_update', args=[self.booking.id, 'COMPLETED']))
        self.assertEqual(response.status_code, 302)
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.status, 'COMPLETED')

    def test_booking_delete_as_owner(self):
        self.http_client.login(username='agent_john', password='password123')
        response = self.http_client.post(reverse('bookings:delete', args=[self.booking.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Booking.objects.filter(id=self.booking.id).exists())

    def test_todays_bookings_redirect(self):
        self.http_client.login(username='agent_john', password='password123')
        response = self.http_client.get(reverse('bookings:today'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('timeframe=today', response.url)