"""
Shipment models for Tobaz Autos.
"""
import uuid
from django.db import models
from django.utils import timezone


class Shipment(models.Model):
    """Shipment model for tracking goods."""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_transit', 'In Transit'),
        ('customs', 'In Customs'),
        ('received', 'Received'),
        ('cancelled', 'Cancelled'),
    ]
    
    SHIPMENT_TYPE_CHOICES = [
        ('loading', 'Loading Abroad'),
        ('receiving', 'Receiving in Nigeria'),
    ]
    
    SHIPPING_METHOD_CHOICES = [
        ('air', 'Air Freight'),
        ('sea', 'Sea Freight'),
        ('land', 'Land Transport'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tracking_number = models.CharField(max_length=100, unique=True, blank=True)
    shipment_type = models.CharField(max_length=20, choices=SHIPMENT_TYPE_CHOICES)
    
    # Origin and destination
    origin_country = models.CharField(max_length=100)
    origin_city = models.CharField(max_length=100, blank=True, null=True)
    destination_country = models.CharField(max_length=100, default='Nigeria')
    destination_city = models.CharField(max_length=100, blank=True, null=True)
    
    # Shipping details
    shipping_method = models.CharField(max_length=20, choices=SHIPPING_METHOD_CHOICES)
    carrier = models.CharField(max_length=100, blank=True, null=True)
    estimated_arrival = models.DateField(blank=True, null=True)
    actual_arrival = models.DateField(blank=True, null=True)
    
    # Costs
    shipping_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    customs_duty = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    insurance_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    other_costs = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Documents
    invoice_file = models.URLField(blank=True, null=True)
    bill_of_lading = models.URLField(blank=True, null=True)
    customs_document = models.URLField(blank=True, null=True)
    other_documents = models.JSONField(default=list, blank=True)
    
    # Notes
    notes = models.TextField(blank=True, null=True)
    
    # Tracking
    created_by = models.ForeignKey(
        'core.User', on_delete=models.SET_NULL, null=True, related_name='shipments_created'
    )
    received_by = models.ForeignKey(
        'core.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='shipments_received'
    )
    received_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'shipments'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.tracking_number} - {self.origin_country} to {self.destination_country}"
    
    def save(self, *args, **kwargs):
        if not self.tracking_number:
            self.tracking_number = self.generate_tracking_number()
        super().save(*args, **kwargs)
    
    def generate_tracking_number(self):
        """Generate unique tracking number."""
        prefix = 'TBA'
        if self.shipment_type == 'loading':
            prefix = 'TBA-LD'
        else:
            prefix = 'TBA-RC'
        
        last_shipment = Shipment.objects.filter(
            tracking_number__startswith=prefix
        ).order_by('-tracking_number').first()
        
        if last_shipment:
            try:
                last_num = int(last_shipment.tracking_number.split('-')[2])
                return f"{prefix}-{last_num + 1:06d}"
            except:
                pass
        return f"{prefix}-000001"
    
    @property
    def total_cost(self):
        """Calculate total shipment cost."""
        return self.shipping_cost + self.customs_duty + self.insurance_cost + self.other_costs
    
    @property
    def is_overdue(self):
        """Check if shipment is overdue."""
        if self.estimated_arrival and self.status not in ['received', 'cancelled']:
            return timezone.now().date() > self.estimated_arrival
        return False
    
    @property
    def days_in_transit(self):
        """Calculate days in transit."""
        if self.status == 'received' and self.actual_arrival:
            return (self.actual_arrival - self.created_at.date()).days
        elif self.status in ['in_transit', 'customs']:
            return (timezone.now().date() - self.created_at.date()).days
        return 0


class ShipmentItem(models.Model):
    """Items in a shipment."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    shipment = models.ForeignKey(
        Shipment, on_delete=models.CASCADE, related_name='items'
    )
    product = models.ForeignKey(
        'inventory.Product', on_delete=models.SET_NULL, null=True, blank=True
    )
    product_name = models.CharField(max_length=200)
    quantity = models.PositiveIntegerField(default=1)
    unit_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    description = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'shipment_items'
    
    def __str__(self):
        return f"{self.product_name} x{self.quantity}"
    
    def save(self, *args, **kwargs):
        self.total_cost = self.quantity * self.unit_cost
        super().save(*args, **kwargs)


class ShipmentTracking(models.Model):
    """Shipment tracking updates."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    shipment = models.ForeignKey(
        Shipment, on_delete=models.CASCADE, related_name='tracking_updates'
    )
    status = models.CharField(max_length=50)
    location = models.CharField(max_length=200, blank=True, null=True)
    description = models.TextField()
    tracking_date = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(
        'core.User', on_delete=models.SET_NULL, null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'shipment_tracking'
        ordering = ['-tracking_date']
    
    def __str__(self):
        return f"{self.shipment.tracking_number} - {self.status}"
