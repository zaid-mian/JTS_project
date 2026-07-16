from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Organization, OwnerProfile, RegistrationRequest

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'username', 'first_name', 'last_name', 'is_email_verified', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('Verification Status', {'fields': ('is_email_verified',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Verification Status', {'fields': ('is_email_verified',)}),
    )


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at')


@admin.register(OwnerProfile)
class OwnerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'organization', 'cnic', 'phone_number', 'country')


@admin.register(RegistrationRequest)
class RegistrationRequestAdmin(admin.ModelAdmin):
    list_display = ('owner_profile', 'status', 'submitted_at', 'reviewed_at')


