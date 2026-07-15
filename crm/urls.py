from django.urls import path
from . import views

app_name = 'crm'

urlpatterns = [
    # 1. Product Listing API (dynamic landing page lookup)
    path('api/products/', views.CRMProductAPIListView.as_view(), name='api_product_list'),

    # 2. Product Detail API (features, plans, and feature limit matrices)
    path('api/products/<slug:slug>/', views.CRMProductAPIDetailView.as_view(), name='api_product_detail'),
]
