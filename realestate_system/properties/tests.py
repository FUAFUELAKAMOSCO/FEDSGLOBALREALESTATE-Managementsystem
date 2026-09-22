from datetime import timedelta
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from accounts.models import User
from properties.models import Property
from contacts.models import Contact
from bookings.models import Booking
from activity.models import ActivityLog


class PropertyModelAndViewsTest(TestCase):
    def setUp(self):
        self.agent = User.objects.create_user(
            username='agent_estate', email='estate@example.com', password='password123', role='AGENT'
        )
        self.property = Property.objects.create(
            title='Prime Property Located Behind Cathedral around Blue Empire',
            slug='prime-property-behind-cathedral-blue-empire-buea',
            subtitle='We are launching the property located behind Cathedral around Blue Empire in Buea, Cameroon.',
            property_type='LAND',
            status='AVAILABLE',
            price=2000000.00,
            currency='FCFA',
            price_prefix='Starting from',
            price_suffix='per 400 m² titled plot',
            area_sqm=400.00,
            location='Behind Cathedral around Blue Empire, Buea, Cameroon',
            city='Buea',
            region='South West Region',
            country='Cameroon',
            assigned_agent=self.agent,
            is_featured=True
        )
        self.http_client = Client()

    def test_property_str_and_price(self):
        self.assertIn('Behind Cathedral', str(self.property))
        self.assertIn('2 000 000 FCFA', self.property.formatted_price)

    def test_landing_page(self):
        response = self.http_client.get(reverse('properties:landing'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Behind Cathedral')
        self.assertContains(response, 'Blue Empire')
        self.property.refresh_from_db()
        self.assertGreaterEqual(self.property.views_count, 1)

    def test_catalog_page(self):
        response = self.http_client.get(reverse('properties:catalog'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Featured Properties')
        self.assertContains(response, 'Behind Cathedral')

    def test_property_inquiry(self):
        data = {
            'full_name': 'Roland Tabot',
            'phone': '679998877',
            'country_code': '+237',
            'email': 'roland@example.com',
            'message': 'Interested in buying 2 plots behind Cathedral around Blue Empire.',
        }
        response = self.http_client.post(
            reverse('properties:inquire', args=[self.property.slug]), data
        )
        self.assertEqual(response.status_code, 302)
        # Verify contact created
        contact = Contact.objects.filter(full_name='Roland Tabot').first()
        self.assertIsNotNone(contact)
        # Verify activity log created
        log = ActivityLog.objects.filter(related_client=contact).first()
        self.assertIsNotNone(log)

    def test_property_book_visit(self):
        visit_date = (timezone.now() + timedelta(days=2)).date()
        data = {
            'full_name': 'Nadege Bih',
            'phone': '+237674443322',
            'email': 'nadege@example.com',
            'visit_date': visit_date.strftime('%Y-%m-%d'),
            'visit_time': '10:00',
            'visit_type': 'SITE_VISIT',
            'notes': 'Would like to walk the boundary perimeter.',
        }
        response = self.http_client.post(
            reverse('properties:book_visit', args=[self.property.slug]), data
        )
        self.assertEqual(response.status_code, 302)
        # Verify contact and booking created
        contact = Contact.objects.filter(full_name='Nadege Bih').first()
        self.assertIsNotNone(contact)
        booking = Booking.objects.filter(client=contact).first()
        self.assertEqual(booking.booking_type, 'SITE_VISIT')

    def test_landing_page_navbar_location(self):
        response = self.http_client.get(reverse('properties:landing'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Mile 18 Junction Buea')

    def test_property_detail_view(self):
        response = self.http_client.get(reverse('properties:detail', args=[self.property.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.property.title)
        self.assertContains(response, 'Complete Property Description')
        self.assertContains(response, 'Official Legal Documentation')
        self.assertContains(response, 'WhatsApp Inquire')

    def test_property_create_view_authenticated(self):
        self.http_client.login(username='agent_estate', password='password123')
        upload_data = {
            'title': 'Luxury Hilltop Parcel at Mile 18 Junction Buea',
            'subtitle': 'Scenic views of Mount Cameroon with verified cadastral plan.',
            'property_type': 'VILLA',
            'status': 'AVAILABLE',
            'is_featured': True,
            'price': 4500000.00,
            'currency': 'FCFA',
            'price_prefix': 'Starting from',
            'price_suffix': 'per 500 m² plot',
            'area_sqm': 500.00,
            'area_display': '500 m² Executive Villa Plot',
            'topography': '100% Level / Flat Topography',
            'location': 'Mile 18 Junction Buea, Cameroon',
            'city': 'Buea',
            'region': 'South West Region',
            'country': 'Cameroon',
            'description': 'Spectacular residential estate ready for immediate construction of executive villas.',
            'featured_image_preset': 'images/villas.jpg',
            'documents_input': 'Chief Attestation: Certified traditional council endorsement\nRegistered Title Deed: Official cadastral deed',
            'features_input': 'Paved road connectivity\nElectricity corridor ready\nPerimeter boundary pillars',
            'landmarks_input': 'Mile 18 Junction | 1 min | Main junction\nRegina Pacis Cathedral | 3 min | Landmark',
        }
        response = self.http_client.post(reverse('properties:create'), upload_data)
        self.assertEqual(response.status_code, 302)
        new_prop = Property.objects.filter(title='Luxury Hilltop Parcel at Mile 18 Junction Buea').first()
        self.assertIsNotNone(new_prop)
        self.assertEqual(new_prop.property_type, 'VILLA')
        self.assertEqual(len(new_prop.documents), 2)
        self.assertEqual(len(new_prop.features), 3)
        self.assertEqual(len(new_prop.landmarks), 2)

    def test_dashboard_properties_section(self):
        self.http_client.login(username='agent_estate', password='password123')
        response = self.http_client.get(reverse('dashboard:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Properties &amp; Estates Portfolio')
        self.assertContains(response, 'Upload New Property')
        self.assertContains(response, 'View Entire Property')
        self.assertContains(response, self.property.title)

