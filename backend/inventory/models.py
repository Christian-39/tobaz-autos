"""
Inventory models for Tobaz Autos.
"""
import uuid
from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    """Product category."""
    
    CATEGORY_TYPES = [
        ('car', 'Car'),
        ('part', 'Part'),
        ('tool', 'Tool'),
        ('oil', 'Oil'),
        ('accessory', 'Accessory'),
        ('other', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    category_type = models.CharField(max_length=20, choices=CATEGORY_TYPES, default='other')
    description = models.TextField(blank=True, null=True)
    icon = models.CharField(max_length=50, blank=True, null=True)
    color = models.CharField(max_length=7, default='#6366f1')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'categories'
        verbose_name_plural = 'Categories'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Product(models.Model):
    """Product model."""
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('discontinued', 'Discontinued'),
    ]
    
    CONDITION_CHOICES = [
        ('new', 'New'),
        ('used', 'Used'),
        ('refurbished', 'Refurbished'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sku = models.CharField(max_length=50, unique=True, blank=True)
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, related_name='products'
    )
    
    # Pricing
    cost_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    selling_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Inventory
    quantity = models.PositiveIntegerField(default=0)
    reorder_level = models.PositiveIntegerField(default=10)
    reorder_quantity = models.PositiveIntegerField(default=50)
    
    # Product details
    brand = models.CharField(max_length=100, blank=True, null=True)
    model = models.CharField(max_length=100, blank=True, null=True)
    year = models.PositiveIntegerField(blank=True, null=True)
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default='new')
    
    # For cars
    mileage = models.PositiveIntegerField(blank=True, null=True)
    fuel_type = models.CharField(max_length=50, blank=True, null=True)
    transmission = models.CharField(max_length=50, blank=True, null=True)
    color = models.CharField(max_length=50, blank=True, null=True)
    vin = models.CharField(max_length=50, blank=True, null=True)
    
    # Media
    featured_image = models.URLField(blank=True, null=True)
    images = models.JSONField(default=list, blank=True)
    
    # SEO
    meta_title = models.CharField(max_length=200, blank=True, null=True)
    meta_description = models.TextField(blank=True, null=True)
    meta_keywords = models.CharField(max_length=500, blank=True, null=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    is_featured = models.BooleanField(default=False)
    
    # Tracking
    created_by = models.ForeignKey(
        'core.User', on_delete=models.SET_NULL, null=True, related_name='products_created'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'products'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.sku} - {self.name}"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        if not self.sku:
            self.sku = self.generate_sku()
        super().save(*args, **kwargs)
    
    def generate_sku(self):
        """Generate unique SKU."""
        prefix = 'PRD'
        if self.category:
            prefix = self.category.name[:3].upper()
        last_product = Product.objects.filter(sku__startswith=prefix).order_by('-sku').first()
        if last_product:
            try:
                last_num = int(last_product.sku.split('-')[1])
                return f"{prefix}-{last_num + 1:06d}"
            except:
                pass
        return f"{prefix}-000001"
    
    @property
    def profit_margin(self):
        """Calculate profit margin."""
        if self.selling_price > 0:
            return ((self.selling_price - self.cost_price) / self.selling_price) * 100
        return 0
    
    @property
    def stock_status(self):
        """Get stock status."""
        if self.quantity == 0:
            return 'out_of_stock'
        elif self.quantity <= self.reorder_level:
            return 'low_stock'
        return 'in_stock'
    
    @property
    def inventory_value(self):
        """Calculate inventory value."""
        return self.quantity * self.cost_price


class InventoryTransaction(models.Model):
    """Inventory transaction log."""
    
    TRANSACTION_TYPES = [
        ('in', 'Stock In'),
        ('out', 'Stock Out'),
        ('adjustment', 'Adjustment'),
        ('return', 'Return'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='transactions'
    )
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    quantity = models.IntegerField()
    previous_quantity = models.PositiveIntegerField()
    new_quantity = models.PositiveIntegerField()
    reference = models.CharField(max_length=100, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(
        'core.User', on_delete=models.SET_NULL, null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'inventory_transactions'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.product.name} - {self.transaction_type} ({self.quantity})"


class Supplier(models.Model):
    """Supplier model."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'suppliers'
        ordering = ['name']
    
    def __str__(self):
        return self.name
