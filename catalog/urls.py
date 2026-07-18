from django.urls import path
from . import views

app_name = 'catalog'

urlpatterns = [
    path('demo/', views.CatalogDemoView.as_view(), name='demo'),
    path('api/products/', views.CatalogProductAPIListView.as_view(), name='api_product_list'),
    path('api/products/<slug:slug>/', views.CatalogProductAPIDetailView.as_view(), name='api_product_detail'),
    path('api/products/<slug:slug>/feedback/', views.ProductFeedbackAPIView.as_view(), name='api_product_feedback'),

    # Services Module Routes
    path('demo/services/', views.CatalogServicesDemoView.as_view(), name='services_demo'),
    path('api/services/', views.CatalogServicesAPIListView.as_view(), name='api_services_list'),
    path('api/services/<slug:slug>/', views.CatalogServicesAPIDetailView.as_view(), name='api_services_detail'),
    path('api/services/<slug:slug>/feedback/', views.ServiceFeedbackAPIView.as_view(), name='api_services_feedback'),
]

