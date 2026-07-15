from django.test import TestCase
from django.urls import reverse
from django.core.exceptions import ValidationError
from catalog.models import Product, Module, PricingPlan, PlanModule

class CatalogAdminWorkflowTest(TestCase):
    def setUp(self):
        # 1. Admin creates Product
        self.product = Product.objects.create(
            name="Sales CRM",
            slug="sales-crm",
            description="CRM SaaS module for lead management and tracking",
            display_order=1
        )

        # 2. Admin adds Modules
        self.module_lead = Module.objects.create(
            product=self.product,
            name="Lead Management",
            code="lead_management",
            description="Allows managing and nurturing leads",
            display_order=1
        )
        self.module_reports = Module.objects.create(
            product=self.product,
            name="Reports",
            code="reports",
            description="Generate performance reports",
            display_order=2
        )

        # 3. Admin creates Pricing Plans
        self.plan_starter = PricingPlan.objects.create(
            product=self.product,
            name="Starter",
            price=19.00,
            billing_cycle="monthly",
            display_order=1
        )
        self.plan_pro = PricingPlan.objects.create(
            product=self.product,
            name="Professional",
            price=49.00,
            billing_cycle="monthly",
            display_order=2
        )

    def test_admin_workflow(self):
        """Verify the creation and relations of the Catalog Admin models"""
        self.assertEqual(Product.objects.count(), 1)
        self.assertEqual(self.product.slug, "sales-crm")

        # Check Modules creation
        self.assertEqual(Module.objects.filter(product=self.product).count(), 2)

        # Check Pricing Plans creation
        self.assertEqual(PricingPlan.objects.filter(product=self.product).count(), 2)

        # 4. Admin attaches modules and limits to pricing plans (PlanModule workflow)
        pf_starter_lead = PlanModule.objects.create(
            plan=self.plan_starter,
            module=self.module_lead,
            is_enabled=True,
            limit_value="500 leads"
        )
        pf_starter_reports = PlanModule.objects.create(
            plan=self.plan_starter,
            module=self.module_reports,
            is_enabled=False
        )

        self.assertEqual(self.plan_starter.modules.count(), 2)

        # Verify values
        starter_lead_relation = PlanModule.objects.get(plan=self.plan_starter, module=self.module_lead)
        self.assertTrue(starter_lead_relation.is_enabled)
        self.assertEqual(starter_lead_relation.limit_value, "500 leads")

    def test_cross_product_validation(self):
        """Verify that a plan cannot link to modules of another product"""
        # Create a second product
        product2 = Product.objects.create(
            name="HRM Suite",
            slug="hrm-suite",
            description="HRM SaaS module",
            display_order=2
        )
        # Create a module under HRM Suite
        module_hrm = Module.objects.create(
            product=product2,
            name="Leave Tracker",
            code="leave_tracker",
            description="Track leave applications",
            display_order=1
        )

        # Attempt to link Starter plan (from Sales CRM) to Leave Tracker (from HRM Suite)
        with self.assertRaises(ValidationError):
            # This should raise ValidationError in full_clean() inside save()
            PlanModule.objects.create(
                plan=self.plan_starter,
                module=module_hrm,
                is_enabled=True
            )


class CatalogProductAPITestCase(TestCase):
    def setUp(self):
        # Create active product
        self.active_product = Product.objects.create(
            name="Sales CRM",
            slug="sales-crm",
            description="Active CRM SaaS module",
            display_order=1
        )
        # Create inactive product
        self.inactive_product = Product.objects.create(
            name="Marketing CRM",
            slug="marketing-crm",
            description="Inactive CRM SaaS module",
            is_active=False,
            display_order=2
        )
        # Add a module to the active product
        self.module = Module.objects.create(
            product=self.active_product,
            name="Lead Tracking",
            code="lead_tracking",
            description="Track leads dynamically",
            display_order=1
        )
        # Add a pricing plan to the active product
        self.plan = PricingPlan.objects.create(
            product=self.active_product,
            name="Pro",
            price=29.99,
            billing_cycle="monthly",
            display_order=1
        )
        # Map module to plan
        self.plan_module = PlanModule.objects.create(
            plan=self.plan,
            module=self.module,
            is_enabled=True,
            limit_value="1000 leads"
        )

    def test_product_list_api(self):
        import json
        url = reverse('catalog:api_product_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        # Only active products listed
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['name'], "Sales CRM")
        self.assertEqual(data[0]['slug'], "sales-crm")
        self.assertEqual(data[0]['status'], "active")

    def test_product_detail_api_success(self):
        import json
        url = reverse('catalog:api_product_detail', kwargs={'slug': 'sales-crm'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertEqual(data['name'], "Sales CRM")
        self.assertEqual(data['slug'], "sales-crm")
        self.assertTrue(data['is_active'])
        
        # Verify modules
        self.assertEqual(len(data['modules']), 1)
        self.assertEqual(data['modules'][0]['code'], "lead_tracking")
        self.assertEqual(data['modules'][0]['name'], "Lead Tracking")
        
        # Verify pricing plans
        self.assertEqual(len(data['pricing_plans']), 1)
        plan_data = data['pricing_plans'][0]
        self.assertEqual(plan_data['name'], "Pro")
        self.assertEqual(plan_data['price'], "29.99")
        self.assertEqual(plan_data['billing_cycle'], "monthly")
        
        # Verify plan modules
        self.assertEqual(len(plan_data['modules']), 1)
        self.assertEqual(plan_data['modules'][0]['code'], "lead_tracking")
        self.assertEqual(plan_data['modules'][0]['is_enabled'], True)
        self.assertEqual(plan_data['modules'][0]['limit_value'], "1000 leads")

    def test_product_detail_api_not_found(self):
        import json
        # Test inactive product
        url_inactive = reverse('catalog:api_product_detail', kwargs={'slug': 'marketing-crm'})
        response = self.client.get(url_inactive)
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.content)
        self.assertEqual(data['error'], "Product not found")

        # Test non-existent product
        url_none = reverse('catalog:api_product_detail', kwargs={'slug': 'does-not-exist'})
        response = self.client.get(url_none)
        self.assertEqual(response.status_code, 404)

    def test_catalog_demo_page_load(self):
        url = reverse('catalog:demo')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "MEMS Platform Packaging Matrix")

