from django.http import JsonResponse, Http404
from django.shortcuts import get_object_or_404
from django.views import View
from catalog.models import Product

class CatalogProductAPIListView(View):
    """
    API View to list all active products.
    """
    def get(self, request, *args, **kwargs):
        products = Product.objects.filter(is_active=True)
        data = []
        for product in products:
            data.append({
                "name": product.name,
                "slug": product.slug,
                "description": product.description,
                "image": f"https://placehold.co/600x400/png?text={product.name.replace(' ', '+')}",
                "status": "active" if product.is_active else "inactive"
            })
        return JsonResponse(data, safe=False)


class CatalogProductAPIDetailView(View):
    """
    API View to fetch details of a specific product, including
    its modules, pricing plans, and plan-specific limits.
    """
    def get(self, request, slug, *args, **kwargs):
        queryset = Product.objects.filter(is_active=True).prefetch_related(
            'modules',
            'plans__plan_modules__module'
        )
        
        try:
            product = get_object_or_404(queryset, slug=slug)
        except Http404:
            return JsonResponse({"error": "Product not found"}, status=404)

        product_modules = list(product.modules.filter(is_active=True))
        modules_data = [
            {
                "name": m.name,
                "code": m.code,
                "description": m.description
            }
            for m in product_modules
        ]

        plans_data = []
        for plan in product.plans.filter(is_active=True):
            plan_modules_map = {pm.module_id: pm for pm in plan.plan_modules.all()}
            
            plan_modules_list = []
            for module in product_modules:
                pm = plan_modules_map.get(module.id)
                if pm:
                    plan_modules_list.append({
                        "code": module.code,
                        "name": module.name,
                        "is_enabled": pm.is_enabled,
                        "limit_value": pm.limit_value
                    })
                else:
                    plan_modules_list.append({
                        "code": module.code,
                        "name": module.name,
                        "is_enabled": False,
                        "limit_value": None
                    })

            plans_data.append({
                "id": plan.id,
                "name": plan.name,
                "price": str(plan.price),
                "currency": plan.currency,
                "billing_cycle": plan.billing_cycle,
                "is_active": plan.is_active,
                "modules": plan_modules_list
            })

        response_data = {
            "name": product.name,
            "slug": product.slug,
            "description": product.description,
            "image": f"https://placehold.co/600x400/png?text={product.name.replace(' ', '+')}",
            "is_active": product.is_active,
            "modules": modules_data,
            "pricing_plans": plans_data
        }
        return JsonResponse(response_data)


from django.views.generic import TemplateView

class CatalogDemoView(TemplateView):
    """
    Serves the HTML/CSS/JS frontend demo page.
    """
    template_name = 'catalog/demo.html'

