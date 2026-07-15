from django.urls import path
from . import views

app_name = 'catalog'

urlpatterns = [
    path('api/products/', views.CatalogProductAPIListView.as_view(), name='api_product_list'),
    path('api/products/<slug:slug>/', views.CatalogProductAPIDetailView.as_view(), name='api_product_detail'),
]
