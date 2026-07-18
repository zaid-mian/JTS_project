import json
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from support.models import ContactMessage

@method_decorator(csrf_exempt, name='dispatch')
class PublicContactAPIView(View):
    """
    Public Contact Form API endpoint for guests to submit support inquiries.
    """
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        name = data.get('name')
        email = data.get('email')
        subject = data.get('subject')
        message = data.get('message')

        if not name or not email or not subject or not message:
            return JsonResponse({"error": "Missing required fields"}, status=400)

        ContactMessage.objects.create(
            name=name,
            email=email,
            subject=subject,
            message=message
        )
        return JsonResponse({"message": "Your contact message has been submitted successfully."}, status=200)
