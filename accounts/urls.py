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

    # Registration and Owner dashboard paths
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='html_login'),
    path('logout/', views.html_logout_view, name='html_logout'),
    path('redirect/', views.redirect_after_login, name='redirect_after_login'),
    path('dashboard/', views.owner_dashboard, name='owner_dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-dashboard/profile/<int:req_id>/', views.owner_profile_detail, name='owner_profile_detail'),
    path('admin-dashboard/approve/<int:req_id>/', views.approve_request, name='approve_request'),
    path('admin-dashboard/reject/<int:req_id>/', views.reject_request, name='reject_request'),
]





