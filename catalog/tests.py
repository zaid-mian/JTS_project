from datetime import timedelta
from django.utils import timezone
from django.test import TestCase
from django.urls import reverse
from django.core.exceptions import ValidationError
from catalog.models import Product, Module, PricingPlan, PlanModule, Service, ServiceFeature, Discount, Feedback
import json

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
        self.assertContains(response, "Packaging Matrix")


import os
import tempfile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings

@override_settings(MEDIA_ROOT=tempfile.gettempdir())
class ProductImageSupportTest(TestCase):
    def setUp(self):
        # Create a small valid GIF/PNG image
        self.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        self.image_file = SimpleUploadedFile("test_product.png", self.small_gif, content_type="image/png")

    def test_product_image_save_and_url(self):
        """Test that a product with an image stores it and the API exposes the absolute URL."""
        product = Product.objects.create(
            name="Cloud ERP",
            slug="cloud-erp",
            description="ERP SaaS product",
            image=self.image_file,
            display_order=3
        )
        
        self.assertTrue(product.image)
        self.assertTrue("test_product" in product.image.url)
        
        # Test List API
        url_list = reverse('catalog:api_product_list')
        response = self.client.get(url_list)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Find our product
        cloud_erp_data = next((item for item in data if item["slug"] == "cloud-erp"), None)
        self.assertIsNotNone(cloud_erp_data)
        self.assertEqual(cloud_erp_data["id"], product.id)
        # Should be absolute URL
        self.assertTrue(cloud_erp_data["image"].startswith("http"))
        self.assertTrue(cloud_erp_data["image"].endswith("/media/products/test_product.png") or "test_product" in cloud_erp_data["image"])

        # Test Detail API
        url_detail = reverse('catalog:api_product_detail', kwargs={'slug': 'cloud-erp'})
        response = self.client.get(url_detail)
        self.assertEqual(response.status_code, 200)
        detail_data = response.json()
        self.assertEqual(detail_data["id"], product.id)
        self.assertTrue(detail_data["image"].startswith("http"))
        self.assertTrue(detail_data["image"].endswith("/media/products/test_product.png") or "test_product" in detail_data["image"])

    def test_product_no_image_returns_null(self):
        """Test that a product without an image returns null in API."""
        product = Product.objects.create(
            name="No Image Product",
            slug="no-image-product",
            description="No image",
            display_order=4
        )
        
        # Test Detail API
        url_detail = reverse('catalog:api_product_detail', kwargs={'slug': 'no-image-product'})
        response = self.client.get(url_detail)
        self.assertEqual(response.status_code, 200)
        detail_data = response.json()
        self.assertEqual(detail_data["id"], product.id)
        self.assertIsNone(detail_data["image"])

    def test_image_format_validation(self):
        """Test that non-image formats are rejected, and valid ones are accepted."""
        # Reject invalid extension (e.g. .txt)
        txt_file = SimpleUploadedFile("fake_image.txt", b"not-an-image", content_type="text/plain")
        product = Product(name="Invalid product", slug="invalid-product", image=txt_file)
        with self.assertRaises(ValidationError):
            product.full_clean()

        # Reject invalid extension even if named as png
        bad_png = SimpleUploadedFile("bad_image.png", b"not-an-image", content_type="image/png")
        product2 = Product(name="Invalid product 2", slug="invalid-product-2", image=bad_png)
        with self.assertRaises(ValidationError):
            product2.full_clean()

        # Reject disallowed extension (GIF) even if valid image data
        valid_gif = SimpleUploadedFile("good_image.gif", self.small_gif, content_type="image/gif")
        product3 = Product(name="Good GIF", slug="good-gif", image=valid_gif)
        with self.assertRaises(ValidationError):
            product3.full_clean()

        # Accept valid extension with valid image data (PNG)
        valid_png = SimpleUploadedFile("good_image.png", self.small_gif, content_type="image/png")
        product4 = Product(name="Good PNG", slug="good-png", image=valid_png)
        product4.full_clean()  # should pass

    def test_image_size_validation(self):
        """Test that image size validation triggers above 5MB."""
        # Create a file just over 5 MB
        large_content = b'0' * (5 * 1024 * 1024 + 1)
        large_file = SimpleUploadedFile("large_image.png", large_content, content_type="image/png")
        product = Product(name="Large image product", slug="large-image-product", image=large_file)
        with self.assertRaises(ValidationError) as ctx:
            product.full_clean()
        self.assertIn("Maximum upload size is 5.0 MB", str(ctx.exception))

    def test_image_cleanup_on_change_and_delete(self):
        """Test that replacing or deleting a product deletes the file from storage."""
        # Create product with image
        product = Product.objects.create(
            name="Clean Product",
            slug="clean-product",
            image=self.image_file
        )
        file_path = product.image.path
        self.assertTrue(os.path.exists(file_path))
        
        # Replace image
        new_image = SimpleUploadedFile("new_product.png", self.small_gif, content_type="image/png")
        product.image = new_image
        product.save()
        
        # Verify old image is deleted
        self.assertFalse(os.path.exists(file_path))
        new_file_path = product.image.path
        self.assertTrue(os.path.exists(new_file_path))
        
        # Delete product
        product.delete()
        
        # Verify new image is also deleted
        self.assertFalse(os.path.exists(new_file_path))


@override_settings(MEDIA_ROOT=tempfile.gettempdir())
class ServicesAPIAndModelTest(TestCase):
    def setUp(self):
        # Create a small valid GIF/PNG image
        self.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        self.image_file = SimpleUploadedFile("test_service.png", self.small_gif, content_type="image/png")
        
        # Create an active service
        self.service = Service.objects.create(
            name="CRM Consultation",
            slug="crm-consultation",
            short_description="Summary CRM consultation",
            full_description="Detailed CRM consultation details...",
            image=self.image_file,
            display_order=1
        )
        # Add features
        self.feat1 = ServiceFeature.objects.create(
            service=self.service,
            name="Online Meeting",
            display_order=1
        )
        self.feat2 = ServiceFeature.objects.create(
            service=self.service,
            name="Strategy Session",
            display_order=2
        )

    def test_services_list_api(self):
        """Test the list API endpoint returned values and status code."""
        url = reverse('catalog:api_services_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['name'], "CRM Consultation")
        self.assertEqual(data[0]['slug'], "crm-consultation")
        self.assertEqual(data[0]['status'], "active")
        self.assertTrue("test_service" in data[0]['image'])

    def test_services_detail_api(self):
        """Test the details API endpoint returned values and features list."""
        url = reverse('catalog:api_services_detail', kwargs={"slug": "crm-consultation"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data['name'], "CRM Consultation")
        self.assertEqual(data['slug'], "crm-consultation")
        self.assertTrue(data['is_active'])
        self.assertEqual(len(data['features']), 2)
        self.assertEqual(data['features'][0]['name'], "Online Meeting")
        self.assertEqual(data['features'][1]['name'], "Strategy Session")

    def test_services_detail_api_not_found(self):
        """Test details API returns 404 for missing slugs."""
        url = reverse('catalog:api_services_detail', kwargs={"slug": "missing-slug"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()['error'], "Service not found")

    def test_service_image_size_validation(self):
        """Test that validation triggers error for file size exceeding 5MB."""
        large_content = b'0' * (5 * 1024 * 1024 + 1)
        large_file = SimpleUploadedFile("large_service.png", large_content, content_type="image/png")
        service = Service(name="Large service", slug="large-service", image=large_file)
        with self.assertRaises(ValidationError) as ctx:
            service.full_clean()
        self.assertIn("Maximum upload size is 5.0 MB", str(ctx.exception))

    def test_service_image_cleanup_on_change_and_delete(self):
        """Test signal cleanups for Service images."""
        service = Service.objects.create(
            name="Cleanup Service",
            slug="cleanup-service",
            image=self.image_file
        )
        file_path = service.image.path
        self.assertTrue(os.path.exists(file_path))
        
        # Replace
        new_image = SimpleUploadedFile("new_service.png", self.small_gif, content_type="image/png")
        service.image = new_image
        service.save()
        
        self.assertFalse(os.path.exists(file_path))
        new_file_path = service.image.path
        self.assertTrue(os.path.exists(new_file_path))
        
        # Delete
        service.delete()
        self.assertFalse(os.path.exists(new_file_path))

    def test_services_demo_page_load(self):
        """Test that services demo page loads correctly."""
        url = reverse('catalog:services_demo')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Professional Services Catalog")


class DiscountSystemAndUnifiedPricingTest(TestCase):
    def setUp(self):
        self.product = Product.objects.create(name="Sales CRM", slug="sales-crm")
        self.service = Service.objects.create(name="Custom Dev", slug="custom-dev")

        # Create pricing plans for product and service
        self.product_plan = PricingPlan.objects.create(
            product=self.product,
            name="Pro Plan",
            price=100.00,
            currency="USD",
            billing_cycle="monthly"
        )
        self.service_plan = PricingPlan.objects.create(
            service=self.service,
            name="Basic Pack",
            price=500.00,
            currency="USD",
            billing_cycle="one_time"
        )

    def test_pricing_plan_exclusivity_validation(self):
        """PricingPlan must target either product or service, not both or neither."""
        # 1. Neither
        plan = PricingPlan(name="Bad Plan", price=50.00)
        with self.assertRaises(ValidationError) as ctx:
            plan.full_clean()
        self.assertIn("A pricing plan must be linked to either a Product or a Service.", str(ctx.exception))

        # 2. Both
        plan2 = PricingPlan(product=self.product, service=self.service, name="Bad Plan", price=50.00)
        with self.assertRaises(ValidationError) as ctx:
            plan2.full_clean()
        self.assertIn("A pricing plan cannot be linked to both a Product and a Service.", str(ctx.exception))

    def test_plan_module_product_constraint(self):
        """PlanModule can only be configured for plans belonging to a Product."""
        module = Module.objects.create(product=self.product, name="Lead Gen", code="leads")
        
        # Valid: plan has product
        pm = PlanModule(plan=self.product_plan, module=module)
        pm.full_clean()  # should not raise

        # Invalid: plan has service (no product)
        pm2 = PlanModule(plan=self.service_plan, module=module)
        with self.assertRaises(ValidationError) as ctx:
            pm2.full_clean()
        self.assertIn("Plan modules can only be configured for plans belonging to a Product.", str(ctx.exception))

    def test_discount_validation_rules(self):
        """Test percentage, fixed bounds, and date chronology validations."""
        # 1. Percentage bounds
        d1 = Discount(pricing_plan=self.product_plan, name="Sale", discount_type="percentage", value=120.00)
        with self.assertRaises(ValidationError) as ctx:
            d1.full_clean()
        self.assertIn("Percentage discount value must be between 0 and 100.", str(ctx.exception))

        # 2. Fixed bounds (exceeding original price)
        d2 = Discount(pricing_plan=self.product_plan, name="Sale", discount_type="fixed", value=150.00)
        with self.assertRaises(ValidationError) as ctx:
            d2.full_clean()
        self.assertIn("Fixed discount amount cannot exceed the pricing plan price", str(ctx.exception))

        # 3. Invalid dates
        now = timezone.now()
        d3 = Discount(
            pricing_plan=self.product_plan,
            name="Sale",
            discount_type="percentage",
            value=10.00,
            start_date=now + timedelta(days=1),
            end_date=now
        )
        with self.assertRaises(ValidationError) as ctx:
            d3.full_clean()
        self.assertIn("Start date must be chronologically before end date.", str(ctx.exception))

    def test_discount_calculations_and_scheduling(self):
        """Test manual overrides and date scheduling calculations."""
        now = timezone.now()
        
        # 1. Inactive discount (manual override)
        d_inactive = Discount.objects.create(
            pricing_plan=self.product_plan,
            name="Inactive",
            discount_type="percentage",
            value=20.00,
            is_active=False
        )
        self.assertEqual(self.product_plan.final_price, 100.00)
        
        # 2. Scheduled active discount (percentage)
        d_active = Discount.objects.create(
            pricing_plan=self.product_plan,
            name="Active",
            discount_type="percentage",
            value=20.00,
            start_date=now - timedelta(days=1),
            end_date=now + timedelta(days=1)
        )
        self.assertEqual(self.product_plan.final_price, 80.00)
        
        # 3. Scheduled future discount (not active yet)
        d_future = Discount.objects.create(
            pricing_plan=self.service_plan,
            name="Future",
            discount_type="fixed",
            value=100.00,
            start_date=now + timedelta(days=1),
            end_date=now + timedelta(days=2)
        )
        self.assertEqual(self.service_plan.final_price, 500.00)

        # 4. Overlap active discount validation (must fail)
        d_better = Discount(
            pricing_plan=self.product_plan,
            name="Better Active",
            discount_type="fixed",
            value=35.00,
            is_active=True
        )
        with self.assertRaises(ValidationError) as ctx:
            d_better.full_clean()
        self.assertIn("overlaps with 'Active'", str(ctx.exception))


class CustomerFeedbackTest(TestCase):
    def setUp(self):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        self.customer = User.objects.create_user(
            username='reviewer@example.com',
            email='reviewer@example.com',
            password='Password123'
        )
        self.other_customer = User.objects.create_user(
            username='otherreview@example.com',
            email='otherreview@example.com',
            password='Password123'
        )
        self.product = Product.objects.create(
            name="Feedback Product",
            slug="feedback-product",
            is_active=True
        )
        self.service = Service.objects.create(
            name="Feedback Service",
            slug="feedback-service",
            is_active=True
        )

    def test_feedback_rating_boundaries(self):
        f = Feedback(user=self.customer, product=self.product, rating=5, comment="Great")
        f.full_clean()

        f_low = Feedback(user=self.customer, product=self.product, rating=0, comment="Bad")
        with self.assertRaises(ValidationError):
            f_low.full_clean()

        f_high = Feedback(user=self.customer, product=self.product, rating=6, comment="Superb")
        with self.assertRaises(ValidationError):
            f_high.full_clean()

    def test_feedback_uniqueness_constraints(self):
        Feedback.objects.create(user=self.customer, product=self.product, rating=4, comment="First")
        
        f_dup = Feedback(user=self.customer, product=self.product, rating=5, comment="Second")
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            f_dup.save()

    def test_feedback_api_upsert_flow(self):
        self.client.login(username='reviewer@example.com', password='Password123')
        url = reverse('catalog:api_product_feedback', kwargs={'slug': self.product.slug})
        
        response = self.client.post(
            url,
            json.dumps({"rating": 4, "comment": "Good start"}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Feedback.objects.count(), 1)
        self.assertEqual(Feedback.objects.first().rating, 4)

        response = self.client.post(
            url,
            json.dumps({"rating": 5, "comment": "Excellent now"}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Feedback.objects.count(), 1)
        self.assertEqual(Feedback.objects.first().rating, 5)

    def test_product_detail_api_feedback_keys(self):
        Feedback.objects.create(user=self.customer, product=self.product, rating=5, comment="Amazing")
        Feedback.objects.create(user=self.other_customer, product=self.product, rating=3, comment="Okay")

        url = reverse('catalog:api_product_detail', kwargs={'slug': self.product.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertEqual(data['average_rating'], 4.0)
        self.assertEqual(data['review_count'], 2)
        self.assertEqual(len(data['reviews']), 2)
        self.assertNotIn("reviewer@example.com", json.dumps(data['reviews']))







