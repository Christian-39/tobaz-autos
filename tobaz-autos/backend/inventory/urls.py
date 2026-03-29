"""
URL configuration for Inventory app.
"""
from django.urls import path
from . import views

urlpatterns = [
    # Categories
    path('categories/', views.CategoryListView.as_view(), name='category-list'),
    path('categories/<uuid:id>/', views.CategoryDetailView.as_view(), name='category-detail'),
    
    # Products
    path('products/', views.ProductListView.as_view(), name='product-list'),
    path('products/<uuid:id>/', views.ProductDetailView.as_view(), name='product-detail'),
    path('products/slug/<slug:slug>/', views.ProductBySlugView.as_view(), name='product-by-slug'),
    path('products/<uuid:id>/upload-image/', views.ProductImageUploadView.as_view(), name='product-upload-image'),
    path('products/<uuid:id>/adjust-stock/', views.StockAdjustmentView.as_view(), name='product-adjust-stock'),
    
    # Stock alerts
    path('products/low-stock/', views.LowStockProductsView.as_view(), name='low-stock-products'),
    path('products/out-of-stock/', views.OutOfStockProductsView.as_view(), name='out-of-stock-products'),
    
    # Inventory transactions
    path('transactions/', views.InventoryTransactionListView.as_view(), name='inventory-transactions'),
    
    # Suppliers
    path('suppliers/', views.SupplierListView.as_view(), name='supplier-list'),
    path('suppliers/<uuid:id>/', views.SupplierDetailView.as_view(), name='supplier-detail'),
]
