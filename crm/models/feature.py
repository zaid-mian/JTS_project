from django.db import models

class Feature(models.Model):
    product = models.ForeignKey(
        'crm.Product',
        on_delete=models.CASCADE,
        related_name='features',
        help_text="The CRM product/module this feature belongs to"
    )
    name = models.CharField(max_length=255, help_text="Short name of the feature (e.g. Lead Management)")
    code = models.SlugField(help_text="Code identifier for permission checks (e.g. lead_management). Unique per product.")
    description = models.TextField(blank=True, help_text="Detailed description of what this feature offers")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('product', 'code')

    def __str__(self):
        return f"{self.product.name} - {self.name}"
