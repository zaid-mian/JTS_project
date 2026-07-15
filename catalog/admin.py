from django.contrib import admin
from .models import Product, Module, PricingPlan, PlanModule

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active', 'display_order', 'created_at')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'description')
    list_filter = ('is_active',)

@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('product', 'name', 'code', 'is_active', 'display_order', 'created_at')
    search_fields = ('name', 'code')
    list_filter = ('product', 'is_active')

class PlanModuleInline(admin.TabularInline):
    model = PlanModule
    extra = 1

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "module":
            plan_id = request.resolver_match.kwargs.get('object_id')
            if plan_id:
                try:
                    plan = PricingPlan.objects.get(pk=plan_id)
                    kwargs["queryset"] = db_field.related_model.objects.filter(product=plan.product)
                except PricingPlan.DoesNotExist:
                    pass
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

@admin.register(PricingPlan)
class PricingPlanAdmin(admin.ModelAdmin):
    list_display = ('product', 'name', 'price', 'currency', 'billing_cycle', 'is_active', 'display_order')
    list_filter = ('product', 'billing_cycle', 'is_active')
    inlines = [PlanModuleInline]
