from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from contacts.models import Contact
from tasks.models import Task

User = get_user_model()


class ContactModelAndSignalTest(TestCase):
    def setUp(self):
        self.agent = User.objects.create_user(
            username='testagent',
            email='agent@example.com',
            password='Password123!',
            role='AGENT'
        )
        self.contact = Contact.objects.create(
            full_name='Alice Dupont',
            phone='+237 670 11 22 33',
            email='alice@example.com',
            source='WEBSITE',
            interest='BUY',
            budget=45000000,
            status='NEW',
            assigned_agent=self.agent,
        )

    def test_contact_str_and_properties(self):
        self.assertEqual(str(self.contact), 'Alice Dupont')
        self.assertEqual(self.contact.clean_phone_number, '237670112233')
        self.assertIn('237670112233', self.contact.whatsapp_url)
        self.assertEqual(self.contact.get_absolute_url(), reverse('contacts:edit', kwargs={'pk': self.contact.pk}))

    def test_status_change_creates_task(self):
        # Update status to VIEWING
        self.contact.status = 'VIEWING'
        self.contact.save()

        task = Task.objects.filter(related_client=self.contact).first()
        self.assertIsNotNone(task)
        self.assertEqual(task.owner, self.agent)
        self.assertIn('Schedule viewing', task.title)
        self.assertEqual(task.priority, 'HIGH')


class ContactViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.agent = User.objects.create_user(
            username='testagent',
            email='agent@example.com',
            password='Password123!',
            role='AGENT'
        )
        self.manager = User.objects.create_user(
            username='testmanager',
            email='manager@example.com',
            password='Password123!',
            role='CEO',
            is_staff=True
        )
        self.contact = Contact.objects.create(
            full_name='Bob Kamga',
            phone='+237 699 00 00 00',
            email='bob@example.com',
            source='WALKIN',
            interest='RENT',
            budget=200000,
            status='NEW',
            assigned_agent=self.agent
        )

    def test_contact_list_unauthenticated(self):
        response = self.client.get(reverse('contacts:list'))
        self.assertEqual(response.status_code, 302)

    def test_contact_list_authenticated(self):
        self.client.force_login(self.agent)
        response = self.client.get(reverse('contacts:list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'contacts/list.html')
        self.assertContains(response, 'Bob Kamga')

    def test_contact_search_and_filters(self):
        self.client.force_login(self.agent)
        # Search match
        res1 = self.client.get(reverse('contacts:list') + '?q=Kamga')
        self.assertEqual(res1.status_code, 200)
        self.assertContains(res1, 'Bob Kamga')
        self.assertIn(self.contact, res1.context['contacts'])

        # Search mismatch
        res2 = self.client.get(reverse('contacts:list') + '?q=NonExistent')
        self.assertEqual(res2.status_code, 200)
        self.assertNotIn(self.contact, res2.context['contacts'])
        self.assertContains(res2, 'No contacts match your query')

        # Status filter
        res3 = self.client.get(reverse('contacts:list') + '?status=CLOSED')
        self.assertEqual(res3.status_code, 200)
        self.assertNotIn(self.contact, res3.context['contacts'])
        self.assertContains(res3, 'No contacts match your query')

    def test_contact_create_view(self):
        self.client.force_login(self.agent)
        get_res = self.client.get(reverse('contacts:create'))
        self.assertEqual(get_res.status_code, 200)

        post_data = {
            'full_name': 'Charlie Fotso',
            'phone': '+237 655 44 33 22',
            'email': 'charlie@example.com',
            'source': 'REFERRAL',
            'interest': 'INVEST',
            'budget': 80000000,
            'status': 'NEW',
            'assigned_agent': self.agent.id,
            'notes': 'Looking for commercial plots in Douala',
        }
        post_res = self.client.post(reverse('contacts:create'), post_data)
        self.assertEqual(post_res.status_code, 302)
        self.assertTrue(Contact.objects.filter(full_name='Charlie Fotso').exists())

    def test_contact_edit_view(self):
        self.client.force_login(self.agent)
        post_data = {
            'full_name': 'Bob Kamga Updated',
            'phone': '+237 699 00 00 00',
            'email': 'bob@example.com',
            'source': 'WALKIN',
            'interest': 'BUY',
            'budget': 35000000,
            'status': 'CONTACTED',
            'assigned_agent': self.agent.id,
            'notes': 'Budget increased',
        }
        res = self.client.post(reverse('contacts:edit', kwargs={'pk': self.contact.pk}), post_data)
        self.assertEqual(res.status_code, 302)
        self.contact.refresh_from_db()
        self.assertEqual(self.contact.full_name, 'Bob Kamga Updated')
        self.assertEqual(self.contact.status, 'CONTACTED')

    def test_contact_delete_view(self):
        self.client.force_login(self.manager)
        del_res = self.client.post(reverse('contacts:delete', kwargs={'pk': self.contact.pk}))
        self.assertEqual(del_res.status_code, 302)
        self.assertFalse(Contact.objects.filter(pk=self.contact.pk).exists())
