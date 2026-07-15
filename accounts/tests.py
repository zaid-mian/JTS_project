import json
from django.core import mail
from django.contrib.auth.tokens import default_token_generator
from django.test import TestCase
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from accounts.models import CustomUser

class AccountsAuthTests(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword123",
            first_name="Test",
            last_name="User"
        )
        self.login_url = reverse('accounts:login')
        self.logout_url = reverse('accounts:logout')

    def test_login_success(self):
        response = self.client.post(
            self.login_url,
            data=json.dumps({"email": "test@example.com", "password": "testpassword123"}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["message"], "Login successful")
        self.assertEqual(data["user"]["email"], "test@example.com")
        self.assertEqual(data["user"]["first_name"], "Test")
        self.assertEqual(data["user"]["last_name"], "User")
        self.assertTrue('_auth_user_id' in self.client.session)

    def test_login_invalid_credentials(self):
        response = self.client.post(
            self.login_url,
            data=json.dumps({"email": "test@example.com", "password": "wrongpassword"}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 401)
        data = response.json()
        self.assertEqual(data["error"], "Invalid email or password")
        self.assertFalse('_auth_user_id' in self.client.session)

    def test_login_missing_fields(self):
        response = self.client.post(
            self.login_url,
            data=json.dumps({"email": "test@example.com"}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data["error"], "Email and password are required")

    def test_logout_success(self):
        self.client.login(username="test@example.com", password="testpassword123")
        self.assertTrue('_auth_user_id' in self.client.session)

        response = self.client.post(self.logout_url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["message"], "Logout successful")
        self.assertFalse('_auth_user_id' in self.client.session)

    def test_logout_not_logged_in(self):
        response = self.client.post(self.logout_url)
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data["error"], "You are not logged in")

    def test_change_password_success(self):
        self.client.login(username="test@example.com", password="testpassword123")
        url = reverse('accounts:change_password')
        response = self.client.post(
            url,
            data=json.dumps({
                "current_password": "testpassword123",
                "new_password": "NewStrongPassword123!",
                "confirm_new_password": "NewStrongPassword123!"
            }),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["message"], "Password changed successfully")
        
        # Verify user can log in with the new password
        self.client.logout()
        login_response = self.client.post(
            self.login_url,
            data=json.dumps({"email": "test@example.com", "password": "NewStrongPassword123!"}),
            content_type="application/json"
        )
        self.assertEqual(login_response.status_code, 200)

    def test_change_password_incorrect_current(self):
        self.client.login(username="test@example.com", password="testpassword123")
        url = reverse('accounts:change_password')
        response = self.client.post(
            url,
            data=json.dumps({
                "current_password": "wrongcurrentpassword",
                "new_password": "NewStrongPassword123!",
                "confirm_new_password": "NewStrongPassword123!"
            }),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data["error"], "Incorrect current password")

    def test_change_password_mismatch(self):
        self.client.login(username="test@example.com", password="testpassword123")
        url = reverse('accounts:change_password')
        response = self.client.post(
            url,
            data=json.dumps({
                "current_password": "testpassword123",
                "new_password": "NewStrongPassword123!",
                "confirm_new_password": "DifferentPassword123!"
            }),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data["error"], "New passwords do not match")

    def test_change_password_unauthenticated(self):
        url = reverse('accounts:change_password')
        response = self.client.post(
            url,
            data=json.dumps({
                "current_password": "testpassword123",
                "new_password": "NewStrongPassword123!",
                "confirm_new_password": "NewStrongPassword123!"
            }),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 401)
        data = response.json()
        self.assertEqual(data["error"], "Authentication required")

    def test_change_password_weak_password(self):
        self.client.login(username="test@example.com", password="testpassword123")
        url = reverse('accounts:change_password')
        response = self.client.post(
            url,
            data=json.dumps({
                "current_password": "testpassword123",
                "new_password": "123",
                "confirm_new_password": "123"
            }),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn("errors", data)

    def test_forgot_password_success(self):
        url = reverse('accounts:forgot_password')
        response = self.client.post(
            url,
            data=json.dumps({"email": "test@example.com"}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["message"], "If an account exists with this email, a password reset link has been sent.")
        
        # Verify email is sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["test@example.com"])
        self.assertIn("Password Reset Request", mail.outbox[0].subject)

    def test_forgot_password_invalid_email(self):
        url = reverse('accounts:forgot_password')
        response = self.client.post(
            url,
            data=json.dumps({"email": "doesnotexist@example.com"}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        # Verify no email is sent to avoid security leak / enumeration
        self.assertEqual(len(mail.outbox), 0)

    def test_password_reset_confirm_get_valid(self):
        uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = default_token_generator.make_token(self.user)
        url = reverse('accounts:password_reset_confirm', kwargs={"uidb64": uidb64, "token": token})
        
        # Must pass follow=True because Django secure flow redirects GET to /set-password/
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Reset Password")
        self.assertContains(response, "Update Password")

    def test_password_reset_confirm_get_invalid(self):
        uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = "invalid-token-123"
        url = reverse('accounts:password_reset_confirm', kwargs={"uidb64": uidb64, "token": token})
        
        # Invalid token does not redirect, renders invalid page directly
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid Reset Link")

    def test_password_reset_confirm_post_success(self):
        uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = default_token_generator.make_token(self.user)
        url = reverse('accounts:password_reset_confirm', kwargs={"uidb64": uidb64, "token": token})
        
        # 1. GET request with follow=True sets the session token
        get_response = self.client.get(url, follow=True)
        self.assertEqual(get_response.status_code, 200)
        
        # 2. Extract the actual redirected /set-password/ URL path
        redirected_url = get_response.redirect_chain[0][0]
        
        # 3. POST the passwords to the redirected URL
        response = self.client.post(
            redirected_url,
            data={
                "new_password1": "NewStrongPassword321!",
                "new_password2": "NewStrongPassword321!"
            },
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        # Verify it redirected to complete view
        self.assertTrue(any(reverse('accounts:password_reset_complete') in r[0] for r in response.redirect_chain))
        
        # Verify user password was changed
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("NewStrongPassword321!"))

    def test_password_reset_confirm_post_mismatch(self):
        uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = default_token_generator.make_token(self.user)
        url = reverse('accounts:password_reset_confirm', kwargs={"uidb64": uidb64, "token": token})
        
        # 1. GET request with follow=True sets the session token
        get_response = self.client.get(url, follow=True)
        self.assertEqual(get_response.status_code, 200)
        
        # 2. Extract the redirected URL
        redirected_url = get_response.redirect_chain[0][0]
        
        # 3. POST mismatched passwords
        response = self.client.post(
            redirected_url,
            data={
                "new_password1": "NewStrongPassword321!",
                "new_password2": "MismatchedPassword123!"
            }
        )
        # Form error does not redirect, returns 200 containing warning text
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "didn’t match")





