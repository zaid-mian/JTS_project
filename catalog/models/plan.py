from django.db import models
from django.core.exceptions import ValidationError

class PricingPlan(models.Model):
    BILLING_CYCLE_CHOICES = [
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
        ('one_time', 'One-time'),
    ]

    product = models.ForeignKey(
        'Product',
        on_delete=models.CASCADE,
        related_name='plans',
        help_text="The product this plan belongs to"
    )
    name = models.CharField(max_length=255, help_text="Name of the pricing plan (e.g. Starter, Professional)")
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Cost of the plan")
    currency = models.CharField(max_length=10, default='USD', help_text="Three-letter currency code")
    billing_cycle = models.CharField(
        max_length=20,
        choices=BILLING_CYCLE_CHOICES,
        default='monthly',
        help_text="Frequency of billing"
    )
    modules = models.ManyToManyField(
        'Module',
        through='PlanModule',
        related_name='plans',
        help_text="Modules included in this pricing plan"
    )
    is_active = models.BooleanField(default=True, db_index=True, help_text="Designates whether this plan is active")
    display_order = models.PositiveIntegerField(default=0, db_index=True, help_text="Order in which this plan is displayed")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('product', 'name')
        ordering = ['display_order', 'id']

    def __str__(self):
        return f"{self.product.name} - {self.name} ({self.get_billing_cycle_display()})"


class PlanModule(models.Model):
    plan = models.ForeignKey('PricingPlan', on_delete=models.CASCADE, related_name='plan_modules')
    module = models.ForeignKey('Module', on_delete=models.CASCADE, related_name='plan_modules')
    is_enabled = models.BooleanField(default=True, help_text="Designates whether this module is active in the plan")
    limit_value = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Custom module limit value if any (e.g. '500 leads', '5 users')"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('plan', 'module')
        ordering = ['id']

    def clean(self):
        super().clean()
        if hasattr(self, 'plan') and hasattr(self, 'module'):
            if self.plan.product_id != self.module.product_id:
                raise ValidationError("A pricing plan can only link to modules belonging to the same product.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        status = "Enabled" if self.is_enabled else "Disabled"
        limit = f" (Limit: {self.limit_value})" if self.limit_value else ""
        return f"{self.plan.name} - {self.module.name}: {status}{limit}"
