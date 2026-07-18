import json
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.core.exceptions import ValidationError
from support.models import Ticket, TicketReply

@method_decorator(csrf_exempt, name='dispatch')
class TicketAPIView(View):
    """
    Handles listing tickets (GET) and creating a new ticket (POST) for authenticated users.
    """
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({"detail": "Authentication credentials were not provided."}, status=401)

        if request.user.is_staff:
            tickets = Ticket.objects.all()
        else:
            tickets = Ticket.objects.filter(user=request.user)

        # Filters
        category = request.GET.get('category')
        status = request.GET.get('status')
        priority = request.GET.get('priority')
        assigned_to = request.GET.get('assigned_to')

        if category:
            tickets = tickets.filter(category=category)
        if status:
            tickets = tickets.filter(status=status)
        if priority:
            tickets = tickets.filter(priority=priority)
        if assigned_to:
            tickets = tickets.filter(assigned_to__email=assigned_to)

        data = [
            {
                "ticket_number": t.ticket_number,
                "subject": t.subject,
                "category": t.category,
                "priority": t.priority,
                "status": t.status,
                "assigned_to": t.assigned_to.email if t.assigned_to else None,
                "updated_at": t.updated_at.isoformat()
            }
            for t in tickets
        ]
        return JsonResponse(data, safe=False, status=200)

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({"detail": "Authentication credentials were not provided."}, status=401)

        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        subject = data.get('subject')
        category = data.get('category', 'general')
        priority = data.get('priority', 'medium')
        message = data.get('message')

        if not subject or not message:
            return JsonResponse({"error": "Subject and message are required fields"}, status=400)

        valid_categories = [c[0] for c in Ticket.CATEGORY_CHOICES]
        valid_priorities = [p[0] for p in Ticket.PRIORITY_CHOICES]

        if category not in valid_categories:
            return JsonResponse({"error": f"Invalid category. Choose from: {', '.join(valid_categories)}"}, status=400)
        if priority not in valid_priorities:
            return JsonResponse({"error": f"Invalid priority. Choose from: {', '.join(valid_priorities)}"}, status=400)

        ticket = Ticket(
            user=request.user,
            subject=subject,
            category=category,
            priority=priority,
            message=message
        )
        try:
            ticket.full_clean()
        except ValidationError as e:
            return JsonResponse({"error": e.message_dict}, status=400)

        ticket.save()

        return JsonResponse({
            "ticket_number": ticket.ticket_number,
            "subject": ticket.subject,
            "category": ticket.category,
            "priority": ticket.priority,
            "status": ticket.status,
            "message": ticket.message,
            "created_at": ticket.created_at.isoformat()
        }, status=201)


@method_decorator(csrf_exempt, name='dispatch')
class TicketDetailAPIView(View):
    """
    Retrieves detail view, replies history thread of a ticket.
    """
    def get(self, request, ticket_number, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({"detail": "Authentication credentials were not provided."}, status=401)

        # Standard users only see their own tickets, staff can see any
        if request.user.is_staff:
            ticket = get_object_or_404(Ticket, ticket_number=ticket_number)
        else:
            ticket = get_object_or_404(Ticket, ticket_number=ticket_number, user=request.user)

        replies_data = [
            {
                "id": r.id,
                "sender_name": r.sender.get_full_name() or r.sender.email,
                "sender_email": r.sender.email,
                "is_staff": r.sender.is_staff,
                "message": r.message,
                "created_at": r.created_at.isoformat()
            }
            for r in ticket.replies.all()
        ]

        return JsonResponse({
            "ticket_number": ticket.ticket_number,
            "subject": ticket.subject,
            "category": ticket.category,
            "priority": ticket.priority,
            "status": ticket.status,
            "message": ticket.message,
            "assigned_to": ticket.assigned_to.email if ticket.assigned_to else None,
            "closed_by": ticket.closed_by.email if ticket.closed_by else None,
            "closed_at": ticket.closed_at.isoformat() if ticket.closed_at else None,
            "created_at": ticket.created_at.isoformat(),
            "updated_at": ticket.updated_at.isoformat(),
            "replies": replies_data
        }, status=200)


@method_decorator(csrf_exempt, name='dispatch')
class TicketReplyAPIView(View):
    """
    Post a new reply to an existing ticket. Reopens resolved/closed tickets when customer replies.
    """
    def post(self, request, ticket_number, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({"detail": "Authentication credentials were not provided."}, status=401)

        if request.user.is_staff:
            ticket = get_object_or_404(Ticket, ticket_number=ticket_number)
        else:
            ticket = get_object_or_404(Ticket, ticket_number=ticket_number, user=request.user)

        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        message = data.get('message')
        if not message:
            return JsonResponse({"error": "Message content is required"}, status=400)

        # Automatic reopen logic if customer replies to resolved/closed ticket
        if not request.user.is_staff and ticket.status in ['resolved', 'closed']:
            ticket.status = 'open'
            ticket.save()

        reply = TicketReply.objects.create(
            ticket=ticket,
            sender=request.user,
            message=message
        )

        return JsonResponse({
            "id": reply.id,
            "sender_email": reply.sender.email,
            "message": reply.message,
            "created_at": reply.created_at.isoformat(),
            "ticket_status": ticket.status
        }, status=201)


@method_decorator(csrf_exempt, name='dispatch')
class TicketStatusAPIView(View):
    """
    Handles status transitions for tickets.
    """
    def post(self, request, ticket_number, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({"detail": "Authentication credentials were not provided."}, status=401)

        if request.user.is_staff:
            ticket = get_object_or_404(Ticket, ticket_number=ticket_number)
        else:
            ticket = get_object_or_404(Ticket, ticket_number=ticket_number, user=request.user)

        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        new_status = data.get('status')
        valid_statuses = [s[0] for s in Ticket.STATUS_CHOICES]

        if new_status not in valid_statuses:
            return JsonResponse({"error": f"Invalid status. Choose from: {', '.join(valid_statuses)}"}, status=400)

        # Permission constraint
        if not request.user.is_staff:
            if new_status != 'closed':
                return JsonResponse({"error": "Customers are only allowed to transition tickets to 'closed'."}, status=400)

        ticket.status = new_status
        if new_status == 'closed':
            # Set closed_by to request.user if closed
            ticket.closed_by = request.user
            ticket.closed_at = timezone.now()

        try:
            ticket.full_clean()
        except ValidationError as e:
            return JsonResponse({"error": e.message_dict}, status=400)

        ticket.save()

        return JsonResponse({
            "ticket_number": ticket.ticket_number,
            "status": ticket.status,
            "closed_by": ticket.closed_by.email if ticket.closed_by else None,
            "closed_at": ticket.closed_at.isoformat() if ticket.closed_at else None
        }, status=200)
