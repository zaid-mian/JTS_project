from django.http import JsonResponse, Http404
from django.shortcuts import get_object_or_404
from django.views import View
from crm.models import Product

class CRMProductAPIListView(View):
    """
    API View to list all active CRM products.
    """
    def get(self, request, *args, **kwargs):
        # Fetch active products from database only
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


class CRMProductAPIDetailView(View):
    """
    API View to fetch details of a specific CRM product, including
    its features, pricing plans, and plan-specific limits.
    """
    def get(self, request, slug, *args, **kwargs):
        # Optimized prefetch query to load all associated features, plans, and limit matrices in 3 query calls.
        # This prevents any N+1 database queries.
        queryset = Product.objects.filter(is_active=True).prefetch_related(
            'features',
            'plans__plan_features__feature'
        )
        
        try:
            product = get_object_or_404(queryset, slug=slug)
        except Http404:
            return JsonResponse({"error": "Product not found"}, status=404)

        product_features = list(product.features.all())
        features_data = [
            {
                "name": f.name,
                "code": f.code,
                "description": f.description
            }
            for f in product_features
        ]

        plans_data = []
        for plan in product.plans.all():
            # Build a lookup dictionary mapping feature_id to PlanFeature relation
            plan_features_map = {pf.feature_id: pf for pf in plan.plan_features.all()}
            
            plan_features_list = []
            for feature in product_features:
                pf = plan_features_map.get(feature.id)
                if pf:
                    plan_features_list.append({
                        "code": feature.code,
                        "name": feature.name,
                        "is_enabled": pf.is_enabled,
                        "limit_value": pf.limit_value
                    })
                else:
                    # Fallback defaults for safety and consistency
                    plan_features_list.append({
                        "code": feature.code,
                        "name": feature.name,
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
                "features": plan_features_list
            })

        response_data = {
            "name": product.name,
            "slug": product.slug,
            "description": product.description,
            "image": f"https://placehold.co/600x400/png?text={product.name.replace(' ', '+')}",
            "is_active": product.is_active,
            "features": features_data,
            "pricing_plans": plans_data
        }
        return JsonResponse(response_data)
