import json
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import (
    PasswordResetConfirmView as DjangoPasswordResetConfirmView,
    PasswordResetCompleteView as DjangoPasswordResetCompleteView,
    INTERNAL_RESET_SESSION_TOKEN
)
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from accounts.models import CustomUser

@method_decorator(csrf_exempt, name='dispatch')
class UserLoginView(View):
    """
    API view to log in a user and establish a secure session.
    """
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)

        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return JsonResponse({"error": "Email and password are required"}, status=400)

        # Authenticate using default model backend (mapped to email)
        user = authenticate(request, username=email, password=password)

        if user is not None:
            if not user.is_active:
                return JsonResponse({"error": "This account is inactive"}, status=403)
            
            # Establish the session
            login(request, user)
            
            return JsonResponse({
                "message": "Login successful",
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                }
            }, status=200)
        else:
            return JsonResponse({"error": "Invalid email or password"}, status=401)


class UserLogoutView(View):
    """
    API view to log out a user and destroy the active session.
    """
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({"error": "You are not logged in"}, status=400)

        logout(request)
        return JsonResponse({"message": "Logout successful"}, status=200)


class ChangePasswordView(View):
    """
    API view for authenticated users to change their password.
    """
    def post(self, request, *args, **kwargs):
        # 1. Enforce authentication
        if not request.user.is_authenticated:
            return JsonResponse({"error": "Authentication required"}, status=401)

        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)

        current_password = data.get("current_password")
        new_password = data.get("new_password")
        confirm_new_password = data.get("confirm_new_password")

        # 2. Field presence check
        if not current_password or not new_password or not confirm_new_password:
            return JsonResponse({"error": "All fields are required"}, status=400)

        # 3. Check current password is correct
        if not request.user.check_password(current_password):
            return JsonResponse({"error": "Incorrect current password"}, status=400)

        # 4. Check new passwords match
        if new_password != confirm_new_password:
            return JsonResponse({"error": "New passwords do not match"}, status=400)

        # 5. Enforce Django strength validation policies
        try:
            validate_password(new_password, user=request.user)
        except ValidationError as e:
            return JsonResponse({"errors": e.messages}, status=400)

        # 6. Save new password and update session key
        request.user.set_password(new_password)
        request.user.save()
        update_session_auth_hash(request, request.user)

        return JsonResponse({"message": "Password changed successfully"}, status=200)


@method_decorator(csrf_exempt, name='dispatch')
class ForgotPasswordView(View):
    """
    API view to request a password reset email containing a token.
    """
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)

        email = data.get("email")
        if not email:
            return JsonResponse({"error": "Email is required"}, status=400)

        # Always return 200 to prevent email enumeration
        success_response = JsonResponse({
            "message": "If an account exists with this email, a password reset link has been sent."
        }, status=200)

        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return success_response

        if not user.is_active:
            return success_response

        # Generate recovery tokens
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        # Build absolute reset path
        reset_path = reverse('accounts:password_reset_confirm', kwargs={'uidb64': uidb64, 'token': token})
        reset_link = request.build_absolute_uri(reset_path)

        subject = "MEMS Platform - Password Reset Request"
        message = (
            f"Hello,\n\n"
            f"You requested a password reset for your MEMS account.\n"
            f"Please click the link below to set a new password:\n\n"
            f"{reset_link}\n\n"
            f"If you did not make this request, you can safely ignore this email.\n\n"
            f"Best regards,\n"
            f"MEMS Platform Security Team"
        )

        send_mail(
            subject,
            message,
            None,
            [user.email],
            fail_silently=False
        )

        return success_response


class PasswordResetConfirmView(DjangoPasswordResetConfirmView):
    """
    Renders the password reset form and handles submission with validation.
    """
    template_name = 'accounts/password_reset_confirm.html'
    success_url = reverse_lazy('accounts:password_reset_complete')




class PasswordResetCompleteView(DjangoPasswordResetCompleteView):
    """
    Renders a success confirmation screen after the password is successfully reset.
    """
    template_name = 'accounts/password_reset_complete.html'


from django.views.generic import TemplateView

class AccountsDemoView(TemplateView):
    """
    Serves the HTML/CSS/JS authentication demo page.
    """
    template_name = 'accounts/demo.html'



