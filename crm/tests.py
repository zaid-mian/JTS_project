from django.test import TestCase
from crm.models import Product, Feature, PricingPlan, PlanFeature

class CRMAdminWorkflowTest(TestCase):
    def setUp(self):
        # 1. Admin creates Product
        self.product = Product.objects.create(
            name="Sales CRM",
            slug="sales-crm",
            description="CRM SaaS module for lead management and tracking"
        )

        # 2. Admin adds Features
        self.feature_lead = Feature.objects.create(
            product=self.product,
            name="Lead Management",
            code="lead_management",
            description="Allows managing and nurturing leads"
        )
        self.feature_reports = Feature.objects.create(
            product=self.product,
            name="Reports",
            code="reports",
            description="Generate performance reports"
        )

        # 3. Admin creates Pricing Plans
        self.plan_starter = PricingPlan.objects.create(
            product=self.product,
            name="Starter",
            price=19.00,
            billing_cycle="monthly"
        )
        self.plan_pro = PricingPlan.objects.create(
            product=self.product,
            name="Professional",
            price=49.00,
            billing_cycle="monthly"
        )
        self.plan_enterprise = PricingPlan.objects.create(
            product=self.product,
            name="Enterprise",
            price=99.00,
            billing_cycle="monthly"
        )

    def test_admin_workflow(self):
        """Verify the creation and relations of the CRM Admin models"""
        # Check Product creation
        self.assertEqual(Product.objects.count(), 1)
        self.assertEqual(self.product.slug, "sales-crm")

        # Check Features creation
        self.assertEqual(Feature.objects.filter(product=self.product).count(), 2)

        # Check Pricing Plans creation
        self.assertEqual(PricingPlan.objects.filter(product=self.product).count(), 3)

        # 4. Admin attaches features and limits to pricing plans (PlanFeature inline workflow)
        # Starter plan: has Lead Management (limit: 500 leads), Reports is not enabled
        pf_starter_lead = PlanFeature.objects.create(
            plan=self.plan_starter,
            feature=self.feature_lead,
            is_enabled=True,
            limit_value="500 leads"
        )
        pf_starter_reports = PlanFeature.objects.create(
            plan=self.plan_starter,
            feature=self.feature_reports,
            is_enabled=False
        )

        # Professional plan: has Lead Management (unlimited), Reports (limit: 10 reports/mo)
        pf_pro_lead = PlanFeature.objects.create(
            plan=self.plan_pro,
            feature=self.feature_lead,
            is_enabled=True,
            limit_value="Unlimited"
        )
        pf_pro_reports = PlanFeature.objects.create(
            plan=self.plan_pro,
            feature=self.feature_reports,
            is_enabled=True,
            limit_value="10/month"
        )

        # Enterprise plan: has Lead Management (unlimited), Reports (unlimited)
        pf_ent_lead = PlanFeature.objects.create(
            plan=self.plan_enterprise,
            feature=self.feature_lead,
            is_enabled=True,
            limit_value="Unlimited"
        )
        pf_ent_reports = PlanFeature.objects.create(
            plan=self.plan_enterprise,
            feature=self.feature_reports,
            is_enabled=True,
            limit_value="Unlimited"
        )

        # Assertions
        self.assertEqual(self.plan_starter.features.count(), 2)
        self.assertEqual(self.plan_pro.features.count(), 2)
        self.assertEqual(self.plan_enterprise.features.count(), 2)

        # Verify custom values
        starter_lead_relation = PlanFeature.objects.get(plan=self.plan_starter, feature=self.feature_lead)
        self.assertTrue(starter_lead_relation.is_enabled)
        self.assertEqual(starter_lead_relation.limit_value, "500 leads")

        starter_reports_relation = PlanFeature.objects.get(plan=self.plan_starter, feature=self.feature_reports)
        self.assertFalse(starter_reports_relation.is_enabled)

        pro_reports_relation = PlanFeature.objects.get(plan=self.plan_pro, feature=self.feature_reports)
        self.assertTrue(pro_reports_relation.is_enabled)
        self.assertEqual(pro_reports_relation.limit_value, "10/month")


class CRMProductAPITestCase(TestCase):
    def setUp(self):
        # Create active product
        self.active_product = Product.objects.create(
            name="Sales CRM",
            slug="sales-crm",
            description="Active CRM SaaS module"
        )
        # Create inactive product
        self.inactive_product = Product.objects.create(
            name="Marketing CRM",
            slug="marketing-crm",
            description="Inactive CRM SaaS module",
            is_active=False
        )
        # Add a feature to the active product
        self.feature = Feature.objects.create(
            product=self.active_product,
            name="Lead Tracking",
            code="lead_tracking",
            description="Track leads dynamically"
        )
        # Add a pricing plan to the active product
        self.plan = PricingPlan.objects.create(
            product=self.active_product,
            name="Pro",
            price=29.99,
            billing_cycle="monthly"
        )
        # Map feature to plan
        self.plan_feature = PlanFeature.objects.create(
            plan=self.plan,
            feature=self.feature,
            is_enabled=True,
            limit_value="1000 leads"
        )

    def test_product_list_api(self):
        from django.urls import reverse
        import json
        url = reverse('crm:api_product_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'application/json')
        
        data = json.loads(response.content)
        # Only the active product should be listed
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['name'], "Sales CRM")
        self.assertEqual(data[0]['slug'], "sales-crm")
        self.assertEqual(data[0]['status'], "active")
        self.assertIn("image", data[0])

    def test_product_detail_api_success(self):
        from django.urls import reverse
        import json
        url = reverse('crm:api_product_detail', kwargs={'slug': 'sales-crm'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'application/json')
        
        data = json.loads(response.content)
        self.assertEqual(data['name'], "Sales CRM")
        self.assertEqual(data['slug'], "sales-crm")
        self.assertTrue(data['is_active'])
        self.assertIn("image", data)
        
        # Verify features
        self.assertEqual(len(data['features']), 1)
        self.assertEqual(data['features'][0]['code'], "lead_tracking")
        self.assertEqual(data['features'][0]['name'], "Lead Tracking")
        
        # Verify pricing plans
        self.assertEqual(len(data['pricing_plans']), 1)
        plan_data = data['pricing_plans'][0]
        self.assertEqual(plan_data['name'], "Pro")
        self.assertEqual(plan_data['price'], "29.99")
        self.assertEqual(plan_data['billing_cycle'], "monthly")
        
        # Verify plan features
        self.assertEqual(len(plan_data['features']), 1)
        self.assertEqual(plan_data['features'][0]['code'], "lead_tracking")
        self.assertEqual(plan_data['features'][0]['is_enabled'], True)
        self.assertEqual(plan_data['features'][0]['limit_value'], "1000 leads")

    def test_product_detail_api_not_found(self):
        from django.urls import reverse
        import json
        # Test inactive product
        url_inactive = reverse('crm:api_product_detail', kwargs={'slug': 'marketing-crm'})
        response = self.client.get(url_inactive)
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.content)
        self.assertEqual(data['error'], "Product not found")

        # Test non-existent product
        url_none = reverse('crm:api_product_detail', kwargs={'slug': 'does-not-exist'})
        response = self.client.get(url_none)
        self.assertEqual(response.status_code, 404)

