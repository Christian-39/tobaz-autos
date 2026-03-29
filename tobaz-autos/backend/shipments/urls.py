"""
URL configuration for Shipments app.
"""
from django.urls import path
from . import views

urlpatterns = [
    # Shipments
    path('', views.ShipmentListView.as_view(), name='shipment-list'),
    path('<uuid:id>/', views.ShipmentDetailView.as_view(), name='shipment-detail'),
    path('<uuid:id>/status/', views.ShipmentStatusUpdateView.as_view(), name='shipment-status'),
    path('<uuid:id>/receive/', views.ReceiveShipmentView.as_view(), name='shipment-receive'),
    path('<uuid:id>/tracking/', views.AddTrackingUpdateView.as_view(), name='shipment-tracking'),
    path('<uuid:id>/items/', views.AddShipmentItemView.as_view(), name='shipment-add-item'),
    path('<uuid:id>/items/<uuid:item_id>/', views.RemoveShipmentItemView.as_view(), name='shipment-remove-item'),
    path('<uuid:id>/documents/', views.ShipmentDocumentUploadView.as_view(), name='shipment-upload-document'),
    
    # Shipment lists
    path('pending/', views.PendingShipmentsView.as_view(), name='pending-shipments'),
    path('overdue/', views.OverdueShipmentsView.as_view(), name='overdue-shipments'),
    
    # Stats
    path('stats/overview/', views.ShipmentStatsView.as_view(), name='shipment-stats'),
]
