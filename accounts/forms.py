from django import forms
from accounts.models import CustomUser

class OwnerRegistrationForm(forms.Form):
    full_name = forms.CharField(max_length=150)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput, min_length=8)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    company_name = forms.CharField(max_length=255)
    phone_number = forms.CharField(max_length=20)
    country = forms.CharField(max_length=100)
    address = forms.CharField(max_length=255, widget=forms.Textarea(attrs={'rows': 2}))
    cnic = forms.CharField(max_length=20, label="CNIC Number")
    logo = forms.ImageField(required=False, label="Company Logo (optional)")

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('password') != cleaned.get('confirm_password'):
            raise forms.ValidationError("Passwords do not match.")
        return cleaned

    def clean_email(self):
        email = self.cleaned_data['email']
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email
