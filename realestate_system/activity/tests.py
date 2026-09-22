from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User
from contacts.models import Contact
from activity.models import ActivityLog


class ActivityModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='agent_claire', email='claire@example.com', password='password123', role='AGENT'
        )
        self.contact = Contact.objects.create(
            full_name='David Ngome', phone='+237675554433', assigned_agent=self.user
        )

    def test_activity_str(self):
        log = ActivityLog.objects.create(
            person=self.user,
            related_client=self.contact,
            action='CALLED',
            summary='Called client to explain plot surveying and chief attestation steps.',
            outcome='Client agreed to visit site on Saturday.'
        )
        self.assertIn('agent_claire', str(log))
        self.assertIn('CALLED', str(log))


class ActivityViewsTest(TestCase):
    def setUp(self):
        self.agent = User.objects.create_user(
            username='agent_mike', email='mike@example.com', password='password123', role='AGENT'
        )
        self.contact = Contact.objects.create(
            full_name='Beatrice Enow', phone='+237678889900', assigned_agent=self.agent
        )
        self.log = ActivityLog.objects.create(
            person=self.agent,
            related_client=self.contact,
            action='WHATSAPP',
            summary='Sent brochure PDF for Prime Property Behind Cathedral.',
            outcome='Read message, requested site visit.'
        )
        self.http_client = Client()

    def test_activity_list_requires_login(self):
        response = self.http_client.get(reverse('activity:list'))
        self.assertEqual(response.status_code, 302)

    def test_activity_list_authenticated(self):
        self.http_client.login(username='agent_mike', password='password123')
        response = self.http_client.get(reverse('activity:list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sent brochure PDF for Prime Property Behind Cathedral.')
        self.assertIn('total_activities', response.context)
        self.assertIn('action_labels_json', response.context)

    def test_activity_create_get(self):
        self.http_client.login(username='agent_mike', password='password123')
        response = self.http_client.get(reverse('activity:create'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)

    def test_activity_create_post(self):
        self.http_client.login(username='agent_mike', password='password123')
        data = {
            'related_client': self.contact.id,
            'action': 'MET',
            'summary': 'Met in office to sign deed documentation.',
            'outcome': 'Signed deed transfer, waiting for notary seal.',
        }
        response = self.http_client.post(reverse('activity:create'), data)
        self.assertEqual(response.status_code, 302)
        new_log = ActivityLog.objects.filter(action='MET').first()
        self.assertIsNotNone(new_log)
        self.assertEqual(new_log.person, self.agent)

    def test_activity_filtering(self):
        self.http_client.login(username='agent_mike', password='password123')
        # Filter matching
        response = self.http_client.get(reverse('activity:list') + '?action=WHATSAPP')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sent brochure PDF')

        # Filter non-matching
        response = self.http_client.get(reverse('activity:list') + '?action=EMAILED')
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Sent brochure PDF')
