from django.db import models

class PricingPlan(models.Model):
    BILLING_CYCLE_CHOICES = [
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
        ('one_time', 'One-time'),
    ]

    product = models.ForeignKey(
        'crm.Product',
        on_delete=models.CASCADE,
        related_name='plans',
        help_text="The CRM product/module this plan belongs to"
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
    features = models.ManyToManyField(
        'crm.Feature',
        through='PlanFeature',
        related_name='plans',
        help_text="Features included in this pricing plan"
    )
    is_active = models.BooleanField(default=True, help_text="Designates whether this plan is active")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.product.name} - {self.name} ({self.get_billing_cycle_display()})"


class PlanFeature(models.Model):
    plan = models.ForeignKey('crm.PricingPlan', on_delete=models.CASCADE, related_name='plan_features')
    feature = models.ForeignKey('crm.Feature', on_delete=models.CASCADE, related_name='plan_features')
    is_enabled = models.BooleanField(default=True, help_text="Designates whether this feature is active in the plan")
    limit_value = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Custom feature limit value if any (e.g. '500 leads', '5 users')"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('plan', 'feature')

    def __str__(self):
        status = "Enabled" if self.is_enabled else "Disabled"
        limit = f" (Limit: {self.limit_value})" if self.limit_value else ""
        return f"{self.plan.name} - {self.feature.name}: {status}{limit}"
