"""
Admin configuration for Inventory app.
"""
from django.contrib import admin
from .models import Category, Product, InventoryTransaction, Supplier


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Category admin configuration."""
    
    list_display = ['name', 'category_type', 'product_count', 'is_active', 'created_at']
    list_filter = ['category_type', 'is_active']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    
    def product_count(self, obj):
        return obj.products.count()


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Product admin configuration."""
    
    list_display = [
        'sku', 'name', 'category', 'selling_price', 'quantity',
        'stock_status', 'status', 'is_featured', 'created_at'
    ]
    list_filter = [
        'category', 'status', 'condition', 'is_featured',
        'created_at'
    ]
    search_fields = ['sku', 'name', 'description', 'brand', 'model', 'vin']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['selling_price', 'quantity', 'status', 'is_featured']
    #date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('sku', 'name', 'slug', 'description', 'category')
        }),
        ('Pricing', {
            'fields': ('cost_price', 'selling_price')
        }),
        ('Inventory', {
            'fields': ('quantity', 'reorder_level', 'reorder_quantity')
        }),
        ('Product Details', {
            'fields': ('brand', 'model', 'year', 'condition')
        }),
        ('Car Details', {
            'fields': ('mileage', 'fuel_type', 'transmission', 'color', 'vin'),
            'classes': ('collapse',)
        }),
        ('Media', {
            'fields': ('featured_image', 'video', 'images')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description', 'meta_keywords'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('status', 'is_featured', 'created_by')
        }),
    )
    
    def stock_status(self, obj):
        return obj.stock_status.replace('_', ' ').title()


@admin.register(InventoryTransaction)
class InventoryTransactionAdmin(admin.ModelAdmin):
    """Inventory transaction admin configuration."""
    
    list_display = [
        'product', 'transaction_type', 'quantity', 'previous_quantity',
        'new_quantity', 'reference', 'created_by', 'created_at'
    ]
    list_filter = ['transaction_type', 'created_at']
    search_fields = ['product__name', 'reference', 'notes']
    readonly_fields = [
        'product', 'transaction_type', 'quantity', 'previous_quantity',
        'new_quantity', 'reference', 'notes', 'created_by', 'created_at'
    ]
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    """Supplier admin configuration."""
    
    list_display = ['name', 'contact_person', 'email', 'phone', 'country', 'is_active']
    list_filter = ['is_active', 'country']
    search_fields = ['name', 'contact_person', 'email', 'phone']
