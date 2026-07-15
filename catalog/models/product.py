from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=255, help_text="Name of the SaaS module/service (e.g. Sales CRM)")
    slug = models.SlugField(unique=True, help_text="Unique slug for URL routing")
    description = models.TextField(blank=True, help_text="Detailed description of the product")
    is_active = models.BooleanField(default=True, db_index=True, help_text="Designates whether this product is active and visible")
    display_order = models.PositiveIntegerField(default=0, db_index=True, help_text="Order in which this product is displayed")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['display_order', 'id']

    def __str__(self):
        return self.name
