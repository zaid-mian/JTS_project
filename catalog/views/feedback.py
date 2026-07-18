import json
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ValidationError
from catalog.models import Product, Service, Feedback
from catalog.utils import can_user_review

@method_decorator(csrf_exempt, name='dispatch')
class ProductFeedbackAPIView(View):
    """
    API view to create or edit feedback for a Product.
    """
    def post(self, request, slug, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({"detail": "Authentication credentials were not provided."}, status=401)

        product = get_object_or_404(Product, slug=slug, is_active=True)

        if not can_user_review(request.user, product):
            return JsonResponse({"error": "You must have owned or subscribed to this item to leave feedback."}, status=403)

        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        rating = data.get('rating')
        comment = data.get('comment', '')

        if rating is None:
            return JsonResponse({"error": "Rating is a required field."}, status=400)

        try:
            rating = int(rating)
        except (ValueError, TypeError):
            return JsonResponse({"error": "Rating must be an integer."}, status=400)

        if rating < 1 or rating > 5:
            return JsonResponse({"error": "Rating must be between 1 and 5."}, status=400)

        feedback, created = Feedback.objects.get_or_create(
            user=request.user,
            product=product,
            defaults={'rating': rating, 'comment': comment}
        )
        if not created:
            feedback.rating = rating
            feedback.comment = comment
            try:
                feedback.full_clean()
            except ValidationError as e:
                return JsonResponse({"error": e.message_dict}, status=400)
            feedback.save()

        status_code = 201 if created else 200
        return JsonResponse({
            "message": "Feedback submitted successfully." if created else "Feedback updated successfully.",
            "rating": feedback.rating,
            "comment": feedback.comment,
            "updated_at": feedback.updated_at.isoformat()
        }, status=status_code)


@method_decorator(csrf_exempt, name='dispatch')
class ServiceFeedbackAPIView(View):
    """
    API view to create or edit feedback for a Service.
    """
    def post(self, request, slug, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({"detail": "Authentication credentials were not provided."}, status=401)

        service = get_object_or_404(Service, slug=slug, is_active=True)

        if not can_user_review(request.user, service):
            return JsonResponse({"error": "You must have owned or subscribed to this item to leave feedback."}, status=403)

        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        rating = data.get('rating')
        comment = data.get('comment', '')

        if rating is None:
            return JsonResponse({"error": "Rating is a required field."}, status=400)

        try:
            rating = int(rating)
        except (ValueError, TypeError):
            return JsonResponse({"error": "Rating must be an integer."}, status=400)

        if rating < 1 or rating > 5:
            return JsonResponse({"error": "Rating must be between 1 and 5."}, status=400)

        feedback, created = Feedback.objects.get_or_create(
            user=request.user,
            service=service,
            defaults={'rating': rating, 'comment': comment}
        )
        if not created:
            feedback.rating = rating
            feedback.comment = comment
            try:
                feedback.full_clean()
            except ValidationError as e:
                return JsonResponse({"error": e.message_dict}, status=400)
            feedback.save()

        status_code = 201 if created else 200
        return JsonResponse({
            "message": "Feedback submitted successfully." if created else "Feedback updated successfully.",
            "rating": feedback.rating,
            "comment": feedback.comment,
            "updated_at": feedback.updated_at.isoformat()
        }, status=status_code)
