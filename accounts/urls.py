from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('auth-demo/', views.AccountsDemoView.as_view(), name='demo'),
    path('api/auth/login/', views.UserLoginView.as_view(), name='login'),
    path('api/auth/logout/', views.UserLogoutView.as_view(), name='logout'),
    path('api/auth/change-password/', views.ChangePasswordView.as_view(), name='change_password'),
    path('api/auth/forgot-password/', views.ForgotPasswordView.as_view(), name='forgot_password'),
    path('auth/reset-password/<str:uidb64>/<str:token>/', views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('auth/reset-password/complete/', views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]



