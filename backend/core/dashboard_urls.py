"""
Dashboard URL configuration.
"""
from django.urls import path
from .dashboard_views import DashboardStatsView, SalesChartView, InventoryChartView

urlpatterns = [
    path('stats/', DashboardStatsView.as_view(), name='dashboard-stats'),
    path('charts/sales/', SalesChartView.as_view(), name='sales-chart'),
    path('charts/inventory/', InventoryChartView.as_view(), name='inventory-chart'),
]
