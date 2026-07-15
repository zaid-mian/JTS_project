from django.contrib import admin
from .models import Product, Feature, PricingPlan, PlanFeature

# Admin Configurations for the CRM SaaS module:

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active', 'created_at')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'description')

@admin.register(Feature)
class FeatureAdmin(admin.ModelAdmin):
    list_display = ('product', 'name', 'code', 'created_at')
    search_fields = ('name', 'code')
    list_filter = ('product',)

class PlanFeatureInline(admin.TabularInline):
    model = PlanFeature
    extra = 1

@admin.register(PricingPlan)
class PricingPlanAdmin(admin.ModelAdmin):
    list_display = ('product', 'name', 'price', 'currency', 'billing_cycle', 'is_active')
    list_filter = ('product', 'billing_cycle', 'is_active')
    inlines = [PlanFeatureInline]


