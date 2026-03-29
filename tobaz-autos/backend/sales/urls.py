"""
URL configuration for Sales app.
"""
from django.urls import path
from . import views

urlpatterns = [
    # Customers
    path('customers/', views.CustomerListView.as_view(), name='customer-list'),
    path('customers/<uuid:id>/', views.CustomerDetailView.as_view(), name='customer-detail'),
    
    # Sales
    path('', views.SaleListView.as_view(), name='sale-list'),
    path('<uuid:id>/', views.SaleDetailView.as_view(), name='sale-detail'),
    path('<uuid:id>/status/', views.SaleStatusUpdateView.as_view(), name='sale-status'),
    path('<uuid:id>/payments/', views.AddPaymentView.as_view(), name='sale-payment'),
    path('<uuid:id>/invoice/', views.CreateInvoiceView.as_view(), name='sale-invoice'),
    
    # Stats
    path('stats/overview/', views.SalesStatsView.as_view(), name='sales-stats'),
    path('stats/chart/', views.SalesChartView.as_view(), name='sales-chart'),
    path('stats/top-customers/', views.TopCustomersView.as_view(), name='top-customers'),
    path('stats/top-products/', views.TopProductsView.as_view(), name='top-products'),
]
