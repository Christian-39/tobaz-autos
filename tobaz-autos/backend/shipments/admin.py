"""
Admin configuration for Shipments app.
"""
from django.contrib import admin
from .models import Shipment, ShipmentItem, ShipmentTracking


class ShipmentItemInline(admin.TabularInline):
    """Shipment item inline."""
    model = ShipmentItem
    extra = 1


class ShipmentTrackingInline(admin.TabularInline):
    """Shipment tracking inline."""
    model = ShipmentTracking
    extra = 0
    readonly_fields = ['created_at']


@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    """Shipment admin configuration."""
    
    list_display = [
        'tracking_number', 'shipment_type', 'origin_country',
        'destination_country', 'status', 'estimated_arrival',
        'total_cost', 'created_at'
    ]
    list_filter = ['shipment_type', 'status', 'shipping_method', 'created_at']
    search_fields = ['tracking_number', 'origin_country', 'carrier', 'notes']
    date_hierarchy = 'created_at'
    inlines = [ShipmentItemInline, ShipmentTrackingInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('tracking_number', 'shipment_type', 'status')
        }),
        ('Route', {
            'fields': (
                ('origin_country', 'origin_city'),
                ('destination_country', 'destination_city')
            )
        }),
        ('Shipping Details', {
            'fields': ('shipping_method', 'carrier', 'estimated_arrival', 'actual_arrival')
        }),
        ('Costs', {
            'fields': ('shipping_cost', 'customs_duty', 'insurance_cost', 'other_costs')
        }),
        ('Documents', {
            'fields': ('invoice_file', 'bill_of_lading', 'customs_document', 'other_documents'),
            'classes': ('collapse',)
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Tracking', {
            'fields': ('created_by', 'received_by', 'received_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ShipmentItem)
class ShipmentItemAdmin(admin.ModelAdmin):
    """Shipment item admin configuration."""
    
    list_display = ['shipment', 'product', 'product_name', 'quantity', 'total_cost']
    list_filter = ['shipment__status']
    search_fields = ['product_name', 'shipment__tracking_number']


@admin.register(ShipmentTracking)
class ShipmentTrackingAdmin(admin.ModelAdmin):
    """Shipment tracking admin configuration."""
    
    list_display = ['shipment', 'status', 'location', 'tracking_date', 'created_by']
    list_filter = ['status', 'tracking_date']
    search_fields = ['shipment__tracking_number', 'description']
    readonly_fields = ['created_at']
