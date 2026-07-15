from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'username', 'first_name', 'last_name', 'is_email_verified', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('Verification Status', {'fields': ('is_email_verified',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Verification Status', {'fields': ('is_email_verified',)}),
    )

