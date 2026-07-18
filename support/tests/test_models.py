from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.utils import timezone
from support.models import ContactMessage, Ticket, TicketReply

User = get_user_model()

class SupportModelTest(TestCase):
    def setUp(self):
        self.customer = User.objects.create_user(
            username='customer@example.com',
            email='customer@example.com',
            password='Password123'
        )
        self.staff_user = User.objects.create_user(
            username='staff@example.com',
            email='staff@example.com',
            password='Password123',
            is_staff=True
        )

    def test_contact_message_creation(self):
        msg = ContactMessage.objects.create(
            name="John Doe",
            email="john@example.com",
            subject="Question",
            message="Help me please."
        )
        self.assertEqual(msg.status, 'unread')
        self.assertTrue(msg.submitted_at)
        self.assertIn("John Doe", str(msg))

    def test_ticket_number_generation_after_save(self):
        t1 = Ticket.objects.create(
            user=self.customer,
            subject="First Ticket",
            category="billing",
            message="Initial issue message text."
        )
        self.assertEqual(t1.ticket_number, "TKT-1001")

        t2 = Ticket.objects.create(
            user=self.customer,
            subject="Second Ticket",
            category="technical",
            message="Another issue message text."
        )
        self.assertEqual(t2.ticket_number, "TKT-1002")

    def test_ticket_assigned_to_staff_validation(self):
        t = Ticket(
            user=self.customer,
            subject="Test Assignment",
            message="Message content",
            assigned_to=self.customer  # not staff
        )
        with self.assertRaises(ValidationError):
            t.full_clean()

        t.assigned_to = self.staff_user
        t.full_clean()  # should not raise

    def test_ticket_closure_tracking(self):
        t = Ticket.objects.create(
            user=self.customer,
            subject="Auto Close Track",
            message="Hello",
            status="open"
        )
        self.assertIsNone(t.closed_at)
        self.assertIsNone(t.closed_by)

        t.status = "closed"
        t.closed_by = self.staff_user
        t.save()

        self.assertIsNotNone(t.closed_at)
        self.assertEqual(t.closed_by, self.staff_user)

        # Re-opening ticket resets closure details
        t.status = "open"
        t.save()
        self.assertIsNone(t.closed_at)
        self.assertIsNone(t.closed_by)
