from django.http import JsonResponse, Http404
from django.shortcuts import get_object_or_404
from django.views import View
from django.views.generic import TemplateView
from catalog.models import Service

class CatalogServicesAPIListView(View):
    """
    API View to list all active services.
    """
    def get(self, request, *args, **kwargs):
        services = Service.objects.filter(is_active=True)
        data = []
        for service in services:
            image_url = request.build_absolute_uri(service.image.url) if service.image else None
            data.append({
                "id": service.id,
                "name": service.name,
                "slug": service.slug,
                "short_description": service.short_description,
                "image": image_url,
                "status": "active" if service.is_active else "inactive"
            })
        return JsonResponse(data, safe=False)


class CatalogServicesAPIDetailView(View):
    """
    API View to fetch details of a specific service, including its features and pricing plans.
    """
    def get(self, request, slug, *args, **kwargs):
        queryset = Service.objects.filter(is_active=True).prefetch_related('features', 'plans__discounts')
        
        try:
            service = get_object_or_404(queryset, slug=slug)
        except Http404:
            return JsonResponse({"error": "Service not found"}, status=404)

        features_data = [
            {
                "id": f.id,
                "name": f.name
            }
            for f in service.features.all()
        ]

        plans_data = []
        for plan in service.plans.filter(is_active=True):
            active_discount = plan.get_active_discount()
            plans_data.append({
                "id": plan.id,
                "name": plan.name,
                "price": str(plan.price),  # backward compatibility
                "original_price": str(plan.price),
                "discount_type": active_discount.discount_type if active_discount else None,
                "discount_value": str(active_discount.value) if active_discount else None,
                "discount_status": "active" if active_discount else "inactive",
                "final_price": str(plan.final_price),
                "currency": plan.currency,
                "billing_cycle": plan.billing_cycle,
                "is_active": plan.is_active
            })

        image_url = request.build_absolute_uri(service.image.url) if service.image else None
        response_data = {
            "id": service.id,
            "name": service.name,
            "slug": service.slug,
            "short_description": service.short_description,
            "full_description": service.full_description,
            "image": image_url,
            "is_active": service.is_active,
            "features": features_data,
            "pricing_plans": plans_data
        }
        return JsonResponse(response_data)


class CatalogServicesDemoView(TemplateView):
    """
    Serves the HTML/CSS/JS services demo page.
    """
    template_name = 'catalog/services_demo.html'
