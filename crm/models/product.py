from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=255, help_text="Name of the CRM module/service (e.g. Sales CRM)")
    slug = models.SlugField(unique=True, help_text="Unique slug for URL routing")
    description = models.TextField(blank=True, help_text="Detailed description of the CRM module")
    is_active = models.BooleanField(default=True, help_text="Designates whether this product is active and visible")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
