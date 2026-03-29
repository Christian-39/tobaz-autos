"""
Sales models for Tobaz Autos.
"""
import uuid
from django.db import models
from django.utils import timezone


class Customer(models.Model):
    """Customer model."""
    
    CUSTOMER_TYPE_CHOICES = [
        ('individual', 'Individual'),
        ('business', 'Business'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer_type = models.CharField(max_length=20, choices=CUSTOMER_TYPE_CHOICES, default='individual')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20)
    alternate_phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    company_name = models.CharField(max_length=200, blank=True, null=True)
    tax_id = models.CharField(max_length=50, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'customers'
        ordering = ['-created_at']
    
    def __str__(self):
        if self.company_name:
            return f"{self.company_name} ({self.get_full_name()})"
        return self.get_full_name()
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def total_purchases(self):
        return self.sales.filter(status='completed').count()
    
    @property
    def total_spent(self):
        from django.db.models import Sum
        total = self.sales.filter(status='completed').aggregate(
            total=Sum('total_amount')
        )['total']
        return total or 0


class Sale(models.Model):
    """Sale/Order model."""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('partial', 'Partial'),
        ('paid', 'Paid'),
        ('refunded', 'Refunded'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('transfer', 'Bank Transfer'),
        ('card', 'Card'),
        ('check', 'Check'),
        ('installment', 'Installment'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order_number = models.CharField(max_length=50, unique=True, blank=True)
    customer = models.ForeignKey(
        Customer, on_delete=models.SET_NULL, null=True, related_name='sales'
    )
    
    # Order details
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='cash')
    
    # Financial
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    shipping_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    profit = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Amounts paid
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    amount_due = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Dates
    order_date = models.DateTimeField(default=timezone.now)
    due_date = models.DateField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    
    # Delivery
    delivery_address = models.TextField(blank=True, null=True)
    delivery_notes = models.TextField(blank=True, null=True)
    
    # Notes
    customer_notes = models.TextField(blank=True, null=True)
    staff_notes = models.TextField(blank=True, null=True)
    
    # Tracking
    created_by = models.ForeignKey(
        'core.User', on_delete=models.SET_NULL, null=True, related_name='sales_created'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'sales'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.order_number} - {self.customer}"
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = self.generate_order_number()
        
        # Calculate totals
        self.calculate_totals()
        
        # Update amount due
        self.amount_due = self.total_amount - self.amount_paid
        
        # Update profit
        self.profit = self.total_amount - self.total_cost - self.tax_amount
        
        super().save(*args, **kwargs)
    
    def generate_order_number(self):
        """Generate unique order number."""
        prefix = 'TBA-SALE'
        last_sale = Sale.objects.filter(
            order_number__startswith=prefix
        ).order_by('-order_number').first()
        
        if last_sale:
            try:
                last_num = int(last_sale.order_number.split('-')[2])
                return f"{prefix}-{last_num + 1:06d}"
            except:
                pass
        return f"{prefix}-000001"
    
    def calculate_totals(self):
        """Calculate order totals from items."""
        items = self.items.all()
        self.subtotal = sum(item.total_price for item in items)
        self.total_cost = sum(item.total_cost for item in items)
        self.total_amount = self.subtotal + self.tax_amount + self.shipping_cost - self.discount_amount
    
    def mark_as_paid(self, amount):
        """Mark sale as paid."""
        self.amount_paid += amount
        if self.amount_paid >= self.total_amount:
            self.payment_status = 'paid'
        else:
            self.payment_status = 'partial'
        self.save()
    
    def complete_sale(self):
        """Complete the sale."""
        self.status = 'completed'
        self.payment_status = 'paid'
        self.completed_at = timezone.now()
        self.save()


class SaleItem(models.Model):
    """Items in a sale."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sale = models.ForeignKey(
        Sale, on_delete=models.CASCADE, related_name='items'
    )
    product = models.ForeignKey(
        'inventory.Product', on_delete=models.SET_NULL, null=True, blank=True
    )
    product_name = models.CharField(max_length=200)
    product_sku = models.CharField(max_length=50, blank=True, null=True)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    unit_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    class Meta:
        db_table = 'sale_items'
    
    def __str__(self):
        return f"{self.product_name} x{self.quantity}"
    
    def save(self, *args, **kwargs):
        self.total_price = (self.unit_price * self.quantity) - self.discount
        self.total_cost = self.unit_cost * self.quantity
        super().save(*args, **kwargs)


class Payment(models.Model):
    """Payment record."""
    
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('transfer', 'Bank Transfer'),
        ('card', 'Card'),
        ('check', 'Check'),
        ('installment', 'Installment'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sale = models.ForeignKey(
        Sale, on_delete=models.CASCADE, related_name='payments'
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    reference_number = models.CharField(max_length=100, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    payment_date = models.DateTimeField(default=timezone.now)
    received_by = models.ForeignKey(
        'core.User', on_delete=models.SET_NULL, null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'payments'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.sale.order_number} - ₦{self.amount}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update sale payment status
        self.sale.mark_as_paid(self.amount)


class Invoice(models.Model):
    """Invoice model."""
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    invoice_number = models.CharField(max_length=50, unique=True, blank=True)
    sale = models.OneToOneField(
        Sale, on_delete=models.CASCADE, related_name='invoice'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    issue_date = models.DateField(default=timezone.now)
    due_date = models.DateField()
    notes = models.TextField(blank=True, null=True)
    terms = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'invoices'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.invoice_number
    
    def save(self, *args, **kwargs):
        if not self.invoice_number:
            self.invoice_number = self.generate_invoice_number()
        super().save(*args, **kwargs)
    
    def generate_invoice_number(self):
        """Generate unique invoice number."""
        prefix = 'TBA-INV'
        last_invoice = Invoice.objects.filter(
            invoice_number__startswith=prefix
        ).order_by('-invoice_number').first()
        
        if last_invoice:
            try:
                last_num = int(last_invoice.invoice_number.split('-')[2])
                return f"{prefix}-{last_num + 1:06d}"
            except:
                pass
        return f"{prefix}-000001"
