from datetime import timedelta
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from accounts.models import User
from contacts.models import Contact
from tasks.models import Task


class TaskModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='agent_tom', email='tom@example.com', password='password123', role='AGENT'
        )
        self.contact = Contact.objects.create(
            full_name='Samuel Eto', phone='+237670001122', assigned_agent=self.user
        )

    def test_task_str(self):
        task = Task.objects.create(
            title='Prepare sales agreement',
            owner=self.user,
            due_date=timezone.now().date() + timedelta(days=1),
            status='TODO'
        )
        self.assertIn('Prepare sales agreement', str(task))
        self.assertIn('To Do', str(task))

    def test_is_overdue_property(self):
        yesterday = timezone.now().date() - timedelta(days=1)
        tomorrow = timezone.now().date() + timedelta(days=1)

        overdue_task = Task.objects.create(
            title='Overdue task', owner=self.user, due_date=yesterday, status='TODO'
        )
        self.assertTrue(overdue_task.is_overdue)

        completed_overdue = Task.objects.create(
            title='Completed overdue task', owner=self.user, due_date=yesterday, status='DONE'
        )
        self.assertFalse(completed_overdue.is_overdue)

        future_task = Task.objects.create(
            title='Future task', owner=self.user, due_date=tomorrow, status='TODO'
        )
        self.assertFalse(future_task.is_overdue)


class TaskViewsTest(TestCase):
    def setUp(self):
        self.agent = User.objects.create_user(
            username='agent_sarah', email='sarah@example.com', password='password123', role='AGENT'
        )
        self.manager = User.objects.create_user(
            username='manager_paul', email='paul@example.com', password='password123', role='CEO'
        )
        self.task = Task.objects.create(
            title='Call client about title deed',
            description='Verify notary appointment time.',
            owner=self.agent,
            due_date=timezone.now().date(),
            priority='HIGH',
            status='TODO',
            created_by=self.manager
        )
        self.http_client = Client()

    def test_task_list_requires_login(self):
        response = self.http_client.get(reverse('tasks:list'))
        self.assertEqual(response.status_code, 302)

    def test_task_list_authenticated(self):
        self.http_client.login(username='agent_sarah', password='password123')
        response = self.http_client.get(reverse('tasks:list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Call client about title deed')
        self.assertIn('total_tasks', response.context)
        self.assertIn('status_labels_json', response.context)

    def test_task_create_get(self):
        self.http_client.login(username='agent_sarah', password='password123')
        response = self.http_client.get(reverse('tasks:create'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)

    def test_task_create_post(self):
        self.http_client.login(username='agent_sarah', password='password123')
        data = {
            'title': 'Sign boundary survey endorsement',
            'description': 'Meet surveyor at site.',
            'owner': self.agent.id,
            'priority': 'URGENT',
            'due_date': timezone.now().date().strftime('%Y-%m-%d'),
            'status': 'TODO',
        }
        response = self.http_client.post(reverse('tasks:create'), data)
        self.assertEqual(response.status_code, 302)
        new_task = Task.objects.filter(title='Sign boundary survey endorsement').first()
        self.assertIsNotNone(new_task)
        self.assertEqual(new_task.created_by, self.agent)

    def test_task_edit(self):
        self.http_client.login(username='agent_sarah', password='password123')
        data = {
            'title': 'Call client about title deed (Updated)',
            'description': 'Updated description',
            'owner': self.agent.id,
            'priority': 'URGENT',
            'due_date': timezone.now().date().strftime('%Y-%m-%d'),
            'status': 'IN_PROGRESS',
        }
        response = self.http_client.post(reverse('tasks:edit', args=[self.task.id]), data)
        self.assertEqual(response.status_code, 302)
        self.task.refresh_from_db()
        self.assertEqual(self.task.title, 'Call client about title deed (Updated)')
        self.assertEqual(self.task.status, 'IN_PROGRESS')

    def test_task_toggle(self):
        self.http_client.login(username='agent_sarah', password='password123')
        response = self.http_client.get(reverse('tasks:toggle', args=[self.task.id]))
        self.assertEqual(response.status_code, 302)
        self.task.refresh_from_db()
        self.assertEqual(self.task.status, 'DONE')
        self.assertIsNotNone(self.task.completed_at)

        # Toggle back
        response = self.http_client.get(reverse('tasks:toggle', args=[self.task.id]))
        self.assertEqual(response.status_code, 302)
        self.task.refresh_from_db()
        self.assertEqual(self.task.status, 'TODO')
        self.assertIsNone(self.task.completed_at)

    def test_task_delete(self):
        self.http_client.login(username='agent_sarah', password='password123')
        response = self.http_client.post(reverse('tasks:delete', args=[self.task.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Task.objects.filter(id=self.task.id).exists())

    def test_task_filter_and_scope(self):
        self.http_client.login(username='agent_sarah', password='password123')
        # Filter by priority
        response = self.http_client.get(reverse('tasks:list') + '?priority=HIGH')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Call client about title deed')

        # Filter by non-matching priority
        response = self.http_client.get(reverse('tasks:list') + '?priority=LOW')
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Call client about title deed')

    def test_task_shortcuts(self):
        self.http_client.login(username='agent_sarah', password='password123')
        r1 = self.http_client.get(reverse('tasks:my_tasks'))
        self.assertEqual(r1.status_code, 302)
        self.assertIn('scope=mine', r1.url)

        r2 = self.http_client.get(reverse('tasks:today'))
        self.assertEqual(r2.status_code, 302)
        self.assertIn('timeframe=today', r2.url)

        r3 = self.http_client.get(reverse('tasks:overdue'))
        self.assertEqual(r3.status_code, 302)
        self.assertIn('timeframe=overdue', r3.url)