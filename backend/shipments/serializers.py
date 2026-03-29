"""
Serializers for Shipments app.
"""
from rest_framework import serializers
from .models import Shipment, ShipmentItem, ShipmentTracking


class ShipmentItemSerializer(serializers.ModelSerializer):
    """Shipment item serializer."""
    
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_sku = serializers.CharField(source='product.sku', read_only=True)
    
    class Meta:
        model = ShipmentItem
        fields = [
            'id', 'product', 'product_name', 'product_sku', 'product_name',
            'quantity', 'unit_cost', 'total_cost', 'description'
        ]


class ShipmentItemCreateSerializer(serializers.ModelSerializer):
    """Shipment item create serializer."""
    
    class Meta:
        model = ShipmentItem
        fields = ['product', 'product_name', 'quantity', 'unit_cost', 'description']


class ShipmentTrackingSerializer(serializers.ModelSerializer):
    """Shipment tracking serializer."""
    
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = ShipmentTracking
        fields = [
            'id', 'status', 'location', 'description', 'tracking_date',
            'created_by', 'created_by_name', 'created_at'
        ]


class ShipmentListSerializer(serializers.ModelSerializer):
    """Shipment list serializer."""
    
    item_count = serializers.IntegerField(source='items.count', read_only=True)
    total_items = serializers.SerializerMethodField()
    is_overdue = serializers.BooleanField(read_only=True)
    days_in_transit = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Shipment
        fields = [
            'id', 'tracking_number', 'shipment_type', 'origin_country',
            'destination_country', 'shipping_method', 'carrier', 'status',
            'estimated_arrival', 'actual_arrival', 'item_count', 'total_items',
            'shipping_cost', 'total_cost', 'is_overdue', 'days_in_transit',
            'created_at'
        ]
    
    def get_total_items(self, obj):
        return sum(item.quantity for item in obj.items.all())


class ShipmentDetailSerializer(serializers.ModelSerializer):
    """Shipment detail serializer."""
    
    items = ShipmentItemSerializer(many=True, read_only=True)
    tracking_updates = ShipmentTrackingSerializer(many=True, read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    received_by_name = serializers.CharField(source='received_by.get_full_name', read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    days_in_transit = serializers.IntegerField(read_only=True)
    total_cost = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    
    class Meta:
        model = Shipment
        fields = [
            'id', 'tracking_number', 'shipment_type', 'origin_country',
            'origin_city', 'destination_country', 'destination_city',
            'shipping_method', 'carrier', 'estimated_arrival', 'actual_arrival',
            'shipping_cost', 'customs_duty', 'insurance_cost', 'other_costs',
            'total_cost', 'status', 'invoice_file', 'bill_of_lading',
            'customs_document', 'other_documents', 'notes', 'items',
            'tracking_updates', 'created_by', 'created_by_name',
            'received_by', 'received_by_name', 'received_at', 'is_overdue',
            'days_in_transit', 'created_at', 'updated_at'
        ]


class ShipmentCreateSerializer(serializers.ModelSerializer):
    """Shipment create serializer."""
    
    items = ShipmentItemCreateSerializer(many=True, required=False)
    
    class Meta:
        model = Shipment
        fields = [
            'shipment_type', 'origin_country', 'origin_city',
            'destination_country', 'destination_city', 'shipping_method',
            'carrier', 'estimated_arrival', 'shipping_cost', 'customs_duty',
            'insurance_cost', 'other_costs', 'notes', 'items'
        ]
    
    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        shipment = Shipment.objects.create(**validated_data)
        
        for item_data in items_data:
            ShipmentItem.objects.create(shipment=shipment, **item_data)
        
        return shipment


class ShipmentUpdateSerializer(serializers.ModelSerializer):
    """Shipment update serializer."""
    
    class Meta:
        model = Shipment
        fields = [
            'origin_country', 'origin_city', 'destination_country',
            'destination_city', 'shipping_method', 'carrier',
            'estimated_arrival', 'shipping_cost', 'customs_duty',
            'insurance_cost', 'other_costs', 'notes'
        ]


class ShipmentStatusUpdateSerializer(serializers.Serializer):
    """Shipment status update serializer."""
    
    status = serializers.ChoiceField(choices=Shipment.STATUS_CHOICES)
    notes = serializers.CharField(required=False, allow_blank=True)


class ReceiveShipmentSerializer(serializers.Serializer):
    """Receive shipment serializer."""
    
    received_at = serializers.DateTimeField(required=False)
    notes = serializers.CharField(required=False, allow_blank=True)


class TrackingUpdateSerializer(serializers.Serializer):
    """Add tracking update serializer."""
    
    status = serializers.CharField(required=True)
    location = serializers.CharField(required=False, allow_blank=True)
    description = serializers.CharField(required=True)
    tracking_date = serializers.DateTimeField(required=False)
