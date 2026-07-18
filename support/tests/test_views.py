from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from support.models import ContactMessage, Ticket, TicketReply
import json

User = get_user_model()

class SupportViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.customer = User.objects.create_user(
            username='customer@example.com',
            email='customer@example.com',
            password='Password123'
        )
        self.other_customer = User.objects.create_user(
            username='other@example.com',
            email='other@example.com',
            password='Password123'
        )
        self.staff_user = User.objects.create_user(
            username='staff@example.com',
            email='staff@example.com',
            password='Password123',
            is_staff=True
        )

    def test_public_contact_submission(self):
        url = reverse('support:contact_api')
        payload = {
            "name": "Jane Guest",
            "email": "jane@example.com",
            "subject": "Plan limits question",
            "message": "Please explain the storage limit on Pro plan."
        }
        response = self.client.post(url, json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn("submitted successfully", response.json()['message'])
        self.assertEqual(ContactMessage.objects.count(), 1)
        self.assertEqual(ContactMessage.objects.first().status, 'unread')

    def test_unauthenticated_ticket_actions_return_401(self):
        url = reverse('support:tickets_api')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 401)

        response = self.client.post(url, json.dumps({}), content_type='application/json')
        self.assertEqual(response.status_code, 401)

    def test_ticket_creation_and_listing(self):
        self.client.login(username='customer@example.com', password='Password123')
        url = reverse('support:tickets_api')

        # Create
        payload = {
            "subject": "Database down",
            "category": "technical",
            "priority": "high",
            "message": "Help, database has crashed."
        }
        response = self.client.post(url, json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data['ticket_number'], "TKT-1001")
        self.assertEqual(data['priority'], "high")

        # List (as customer)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        tickets_list = response.json()
        self.assertEqual(len(tickets_list), 1)
        self.assertEqual(tickets_list[0]['ticket_number'], "TKT-1001")
        self.assertEqual(tickets_list[0]['priority'], "high")

    def test_ticket_list_restricted_to_owner(self):
        # Create a ticket for self.customer
        Ticket.objects.create(
            user=self.customer,
            subject="Customer Ticket",
            message="Hello"
        )
        # Login other customer
        self.client.login(username='other@example.com', password='Password123')
        url = reverse('support:tickets_api')
        response = self.client.get(url)
        self.assertEqual(len(response.json()), 0)

        # Login staff
        self.client.login(username='staff@example.com', password='Password123')
        response = self.client.get(url)
        self.assertEqual(len(response.json()), 1)

    def test_ticket_detail_restricted_to_owner(self):
        t = Ticket.objects.create(
            user=self.customer,
            subject="Customer Detail Ticket",
            message="Initial details"
        )
        url = reverse('support:ticket_detail_api', kwargs={'ticket_number': t.ticket_number})

        # Try unauthenticated
        response = self.client.get(url)
        self.assertEqual(response.status_code, 401)

        # Try other customer
        self.client.login(username='other@example.com', password='Password123')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

        # Try owner
        self.client.login(username='customer@example.com', password='Password123')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['message'], "Initial details")

    def test_controlled_lifecycle_transitions(self):
        t = Ticket.objects.create(
            user=self.customer,
            subject="Workflow Ticket",
            message="Test"
        )
        url = reverse('support:ticket_status_api', kwargs={'ticket_number': t.ticket_number})

        # Customer try to set 'in_progress' (should fail)
        self.client.login(username='customer@example.com', password='Password123')
        response = self.client.post(url, json.dumps({"status": "in_progress"}), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn("only allowed to transition tickets to 'closed'", response.json()['error'])

        # Customer closes their own ticket (should succeed)
        response = self.client.post(url, json.dumps({"status": "closed"}), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        t.refresh_from_db()
        self.assertEqual(t.status, "closed")
        self.assertEqual(t.closed_by, self.customer)
        self.assertIsNotNone(t.closed_at)

        # Staff can set any status
        self.client.login(username='staff@example.com', password='Password123')
        response = self.client.post(url, json.dumps({"status": "in_progress"}), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        t.refresh_from_db()
        self.assertEqual(t.status, "in_progress")
        self.assertIsNone(t.closed_by)

    def test_auto_reopen_on_resolved_ticket_reply(self):
        t = Ticket.objects.create(
            user=self.customer,
            subject="Resolved Thread",
            message="Test",
            status="resolved"
        )
        reply_url = reverse('support:ticket_reply_api', kwargs={'ticket_number': t.ticket_number})

        # Customer replies to resolved ticket
        self.client.login(username='customer@example.com', password='Password123')
        payload = {"message": "Actually, it's not resolved yet."}
        response = self.client.post(reply_url, json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 201)

        t.refresh_from_db()
        self.assertEqual(t.status, "open")
        self.assertEqual(t.replies.count(), 1)
