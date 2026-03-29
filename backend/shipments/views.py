"""
Views for Shipments app.
"""
from rest_framework import generics, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q, Sum
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from .models import Shipment, ShipmentItem, ShipmentTracking
from .serializers import (
    ShipmentListSerializer, ShipmentDetailSerializer, ShipmentCreateSerializer,
    ShipmentUpdateSerializer, ShipmentStatusUpdateSerializer, ReceiveShipmentSerializer,
    TrackingUpdateSerializer, ShipmentItemSerializer, ShipmentTrackingSerializer
)
from core.utils import log_activity, upload_to_backblaze
from inventory.models import Product, InventoryTransaction


class ShipmentListView(generics.ListCreateAPIView):
    """List and create shipments."""
    
    queryset = Shipment.objects.all()
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    search_fields = ['tracking_number', 'origin_country', 'carrier', 'notes']
    filterset_fields = ['shipment_type', 'status', 'shipping_method']
    ordering_fields = ['created_at', 'estimated_arrival']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ShipmentCreateSerializer
        return ShipmentListSerializer
    
    def perform_create(self, serializer):
        shipment = serializer.save(created_by=self.request.user)
        log_activity(
            self.request.user, 'create', 'Shipment', str(shipment.id),
            f'Created shipment {shipment.tracking_number}', self.request
        )


class ShipmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a shipment."""
    
    queryset = Shipment.objects.all()
    lookup_field = 'id'
    
    def get_serializer_class(self):
        if self.request.method == 'PUT' or self.request.method == 'PATCH':
            return ShipmentUpdateSerializer
        return ShipmentDetailSerializer
    
    def perform_update(self, serializer):
        shipment = serializer.save()
        log_activity(
            self.request.user, 'update', 'Shipment', str(shipment.id),
            f'Updated shipment {shipment.tracking_number}', self.request
        )
    
    def perform_destroy(self, instance):
        log_activity(
            self.request.user, 'delete', 'Shipment', str(instance.id),
            f'Deleted shipment {instance.tracking_number}', self.request
        )
        instance.delete()


class ShipmentStatusUpdateView(APIView):
    """Update shipment status."""
    
    def post(self, request, pk):
        try:
            shipment = Shipment.objects.get(id=pk)
        except Shipment.DoesNotExist:
            return Response(
                {'error': 'Shipment not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = ShipmentStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        old_status = shipment.status
        new_status = serializer.validated_data['status']
        notes = serializer.validated_data.get('notes', '')
        
        shipment.status = new_status
        shipment.save()
        
        # Add tracking update
        ShipmentTracking.objects.create(
            shipment=shipment,
            status=new_status,
            description=f'Status changed from {old_status} to {new_status}. {notes}',
            created_by=request.user
        )
        
        log_activity(
            request.user, 'update', 'Shipment', str(shipment.id),
            f'Updated shipment status: {old_status} -> {new_status}', request
        )
        
        return Response({
            'message': 'Status updated successfully',
            'old_status': old_status,
            'new_status': new_status
        })


class ReceiveShipmentView(APIView):
    """Mark shipment as received."""
    
    def post(self, request, pk):
        try:
            shipment = Shipment.objects.get(id=pk)
        except Shipment.DoesNotExist:
            return Response(
                {'error': 'Shipment not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if shipment.status == 'received':
            return Response(
                {'error': 'Shipment already received'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = ReceiveShipmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        received_at = serializer.validated_data.get('received_at', timezone.now())
        notes = serializer.validated_data.get('notes', '')
        
        shipment.status = 'received'
        shipment.actual_arrival = received_at.date() if hasattr(received_at, 'date') else received_at
        shipment.received_by = request.user
        shipment.received_at = received_at
        shipment.save()
        
        # Update inventory for each item
        for item in shipment.items.all():
            if item.product:
                product = item.product
                previous_quantity = product.quantity
                product.quantity += item.quantity
                product.save()
                
                # Create inventory transaction
                InventoryTransaction.objects.create(
                    product=product,
                    transaction_type='in',
                    quantity=item.quantity,
                    previous_quantity=previous_quantity,
                    new_quantity=product.quantity,
                    reference=shipment.tracking_number,
                    notes=f'Received from shipment {shipment.tracking_number}',
                    created_by=request.user
                )
        
        # Add tracking update
        ShipmentTracking.objects.create(
            shipment=shipment,
            status='received',
            location=shipment.destination_city or shipment.destination_country,
            description=f'Shipment received. {notes}',
            created_by=request.user
        )
        
        log_activity(
            request.user, 'update', 'Shipment', str(shipment.id),
            f'Received shipment {shipment.tracking_number}', request
        )
        
        return Response({
            'message': 'Shipment received successfully',
            'received_at': shipment.received_at
        })


class AddTrackingUpdateView(APIView):
    """Add tracking update to shipment."""
    
    def post(self, request, pk):
        try:
            shipment = Shipment.objects.get(id=pk)
        except Shipment.DoesNotExist:
            return Response(
                {'error': 'Shipment not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = TrackingUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        tracking = ShipmentTracking.objects.create(
            shipment=shipment,
            status=serializer.validated_data['status'],
            location=serializer.validated_data.get('location', ''),
            description=serializer.validated_data['description'],
            tracking_date=serializer.validated_data.get('tracking_date', timezone.now()),
            created_by=request.user
        )
        
        log_activity(
            request.user, 'create', 'ShipmentTracking', str(tracking.id),
            f'Added tracking update for {shipment.tracking_number}', request
        )
        
        return Response(ShipmentTrackingSerializer(tracking).data)


class AddShipmentItemView(APIView):
    """Add item to shipment."""
    
    def post(self, request, pk):
        try:
            shipment = Shipment.objects.get(id=pk)
        except Shipment.DoesNotExist:
            return Response(
                {'error': 'Shipment not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if shipment.status == 'received':
            return Response(
                {'error': 'Cannot add items to received shipment'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        product_id = request.data.get('product')
        product_name = request.data.get('product_name')
        quantity = request.data.get('quantity', 1)
        unit_cost = request.data.get('unit_cost', 0)
        description = request.data.get('description', '')
        
        product = None
        if product_id:
            try:
                product = Product.objects.get(id=product_id)
                if not product_name:
                    product_name = product.name
            except Product.DoesNotExist:
                pass
        
        item = ShipmentItem.objects.create(
            shipment=shipment,
            product=product,
            product_name=product_name,
            quantity=quantity,
            unit_cost=unit_cost,
            description=description
        )
        
        log_activity(
            request.user, 'create', 'ShipmentItem', str(item.id),
            f'Added item to shipment {shipment.tracking_number}', request
        )
        
        return Response(ShipmentItemSerializer(item).data, status=status.HTTP_201_CREATED)


class RemoveShipmentItemView(APIView):
    """Remove item from shipment."""
    
    def delete(self, request, pk, item_id):
        try:
            shipment = Shipment.objects.get(id=pk)
            item = ShipmentItem.objects.get(id=item_id, shipment=shipment)
        except (Shipment.DoesNotExist, ShipmentItem.DoesNotExist):
            return Response(
                {'error': 'Item not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if shipment.status == 'received':
            return Response(
                {'error': 'Cannot remove items from received shipment'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        log_activity(
            request.user, 'delete', 'ShipmentItem', str(item.id),
            f'Removed item from shipment {shipment.tracking_number}', request
        )
        
        item.delete()
        return Response({'message': 'Item removed successfully'})


class ShipmentDocumentUploadView(APIView):
    """Upload shipment document."""
    
    def post(self, request, pk):
        try:
            shipment = Shipment.objects.get(id=pk)
        except Shipment.DoesNotExist:
            return Response(
                {'error': 'Shipment not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        document_type = request.data.get('document_type', 'other')
        if 'document' not in request.FILES:
            return Response(
                {'error': 'No document provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        document = request.FILES['document']
        document_url = upload_to_backblaze(document, f'shipments/{shipment.id}/documents')
        
        if not document_url:
            return Response(
                {'error': 'Failed to upload document'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Update shipment with document URL
        if document_type == 'invoice':
            shipment.invoice_file = document_url
        elif document_type == 'bill_of_lading':
            shipment.bill_of_lading = document_url
        elif document_type == 'customs':
            shipment.customs_document = document_url
        else:
            if not shipment.other_documents:
                shipment.other_documents = []
            shipment.other_documents.append(document_url)
        
        shipment.save()
        
        log_activity(
            request.user, 'update', 'Shipment', str(shipment.id),
            f'Uploaded {document_type} document for {shipment.tracking_number}', request
        )
        
        return Response({'document_url': document_url})


class PendingShipmentsView(generics.ListAPIView):
    """Get pending shipments."""
    
    serializer_class = ShipmentListSerializer
    
    def get_queryset(self):
        return Shipment.objects.filter(
            status__in=['pending', 'in_transit', 'customs']
        ).order_by('estimated_arrival')


class OverdueShipmentsView(generics.ListAPIView):
    """Get overdue shipments."""
    
    serializer_class = ShipmentListSerializer
    
    def get_queryset(self):
        today = timezone.now().date()
        return Shipment.objects.filter(
            estimated_arrival__lt=today,
            status__in=['pending', 'in_transit', 'customs']
        ).order_by('estimated_arrival')


class ShipmentStatsView(APIView):
    """Get shipment statistics."""
    
    def get(self, request):
        today = timezone.now().date()
        
        stats = {
            'total_shipments': Shipment.objects.count(),
            'pending': Shipment.objects.filter(status='pending').count(),
            'in_transit': Shipment.objects.filter(status='in_transit').count(),
            'in_customs': Shipment.objects.filter(status='customs').count(),
            'received_this_month': Shipment.objects.filter(
                status='received',
                received_at__month=today.month,
                received_at__year=today.year
            ).count(),
            'overdue': Shipment.objects.filter(
                estimated_arrival__lt=today,
                status__in=['pending', 'in_transit', 'customs']
            ).count(),
            'total_cost_this_month': Shipment.objects.filter(
                created_at__month=today.month,
                created_at__year=today.year
            ).aggregate(total=Sum('total_cost'))['total'] or 0,
        }
        
        return Response(stats)
