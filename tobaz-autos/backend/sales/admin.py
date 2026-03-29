"""
Admin configuration for Sales app.
"""
from django.contrib import admin
from .models import Customer, Sale, SaleItem, Payment, Invoice


class SaleItemInline(admin.TabularInline):
    """Sale item inline."""
    model = SaleItem
    extra = 1


class PaymentInline(admin.TabularInline):
    """Payment inline."""
    model = Payment
    extra = 0
    readonly_fields = ['created_at']


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    """Customer admin configuration."""
    
    list_display = [
        'get_full_name', 'customer_type', 'email', 'phone',
        'company_name', 'is_active', 'created_at'
    ]
    list_filter = ['customer_type', 'is_active', 'created_at']
    search_fields = ['first_name', 'last_name', 'email', 'phone', 'company_name']
    date_hierarchy = 'created_at'


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    """Sale admin configuration."""
    
    list_display = [
        'order_number', 'customer', 'total_amount', 'profit',
        'status', 'payment_status', 'order_date'
    ]
    list_filter = ['status', 'payment_status', 'payment_method', 'order_date']
    search_fields = ['order_number', 'customer__first_name', 'customer__last_name']
    date_hierarchy = 'order_date'
    inlines = [SaleItemInline, PaymentInline]
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'customer', 'status', 'payment_status', 'payment_method')
        }),
        ('Financial', {
            'fields': (
                'subtotal', 'tax_amount', 'discount_amount',
                'shipping_cost', 'total_amount', 'total_cost', 'profit'
            )
        }),
        ('Payment', {
            'fields': ('amount_paid', 'amount_due')
        }),
        ('Dates', {
            'fields': ('order_date', 'due_date', 'completed_at')
        }),
        ('Delivery', {
            'fields': ('delivery_address', 'delivery_notes'),
            'classes': ('collapse',)
        }),
        ('Notes', {
            'fields': ('customer_notes', 'staff_notes'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['profit', 'amount_due']


@admin.register(SaleItem)
class SaleItemAdmin(admin.ModelAdmin):
    """Sale item admin configuration."""
    
    list_display = ['sale', 'product', 'product_name', 'quantity', 'total_price']
    list_filter = ['sale__status']
    search_fields = ['product_name', 'sale__order_number']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """Payment admin configuration."""
    
    list_display = ['sale', 'amount', 'payment_method', 'payment_date', 'received_by']
    list_filter = ['payment_method', 'payment_date']
    search_fields = ['sale__order_number', 'reference_number']
    date_hierarchy = 'payment_date'


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    """Invoice admin configuration."""
    
    list_display = ['invoice_number', 'sale', 'status', 'issue_date', 'due_date']
    list_filter = ['status', 'issue_date']
    search_fields = ['invoice_number', 'sale__order_number']
    date_hierarchy = 'issue_date'
