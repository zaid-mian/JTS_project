from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone

class Discount(models.Model):
    DISCOUNT_TYPE_CHOICES = [
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount'),
    ]

    name = models.CharField(max_length=255, help_text="Name of the discount (e.g. Winter Sale)")
    discount_type = models.CharField(
        max_length=20,
        choices=DISCOUNT_TYPE_CHOICES,
        default='percentage',
        help_text="Type of discount (Percentage or Fixed Amount)"
    )
    value = models.DecimalField(max_digits=10, decimal_places=2, help_text="Discount value (percentage e.g. 20.00 or amount e.g. 50.00)")
    is_active = models.BooleanField(default=True, help_text="Manually enable/disable the discount")
    start_date = models.DateTimeField(blank=True, null=True, help_text="Start date/time of the discount (optional)")
    end_date = models.DateTimeField(blank=True, null=True, help_text="End date/time of the discount (optional)")
    
    pricing_plan = models.ForeignKey(
        'PricingPlan',
        on_delete=models.CASCADE,
        related_name='discounts',
        help_text="The pricing plan this discount applies to"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def is_currently_active(self):
        if not self.is_active:
            return False
        
        now = timezone.now()
        if self.start_date and now < self.start_date:
            return False
        if self.end_date and now > self.end_date:
            return False
            
        return True

    def clean(self):
        if self.value is not None:
            from decimal import Decimal
            self.value = Decimal(str(self.value)).quantize(Decimal('0.01'))
        super().clean()
        
        # Date range validation
        if self.start_date and self.end_date:
            if self.start_date >= self.end_date:
                raise ValidationError("Start date must be chronologically before end date.")

        # Value bounds validation
        if self.discount_type == 'percentage':
            if self.value <= 0 or self.value > 100:
                raise ValidationError("Percentage discount value must be between 0 and 100.")
        elif self.discount_type == 'fixed':
            if self.value <= 0:
                raise ValidationError("Fixed discount value must be greater than 0.")
            
            # Check value does not exceed plan price
            if hasattr(self, 'pricing_plan') and self.pricing_plan:
                if self.value > self.pricing_plan.price:
                    raise ValidationError(f"Fixed discount amount cannot exceed the pricing plan price ({self.pricing_plan.price} {self.pricing_plan.currency}).")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - {self.get_discount_type_display()} ({self.value}) for {self.pricing_plan}"
