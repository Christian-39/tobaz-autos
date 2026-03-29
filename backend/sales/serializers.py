"""
Serializers for Sales app.
"""
from rest_framework import serializers
from .models import Customer, Sale, SaleItem, Payment, Invoice


class CustomerSerializer(serializers.ModelSerializer):
    """Customer serializer."""
    
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    total_purchases = serializers.IntegerField(read_only=True)
    total_spent = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    
    class Meta:
        model = Customer
        fields = [
            'id', 'customer_type', 'first_name', 'last_name', 'full_name',
            'email', 'phone', 'alternate_phone', 'address', 'city', 'state',
            'company_name', 'tax_id', 'notes', 'is_active',
            'total_purchases', 'total_spent', 'created_at'
        ]


class CustomerCreateSerializer(serializers.ModelSerializer):
    """Customer create serializer."""
    
    class Meta:
        model = Customer
        fields = [
            'customer_type', 'first_name', 'last_name', 'email', 'phone',
            'alternate_phone', 'address', 'city', 'state', 'company_name',
            'tax_id', 'notes'
        ]


class SaleItemSerializer(serializers.ModelSerializer):
    """Sale item serializer."""
    
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_image = serializers.CharField(source='product.featured_image', read_only=True)
    
    class Meta:
        model = SaleItem
        fields = [
            'id', 'product', 'product_name', 'product_image', 'product_sku',
            'quantity', 'unit_price', 'unit_cost', 'total_price', 'total_cost', 'discount'
        ]


class SaleItemCreateSerializer(serializers.ModelSerializer):
    """Sale item create serializer."""
    
    class Meta:
        model = SaleItem
        fields = ['product', 'quantity', 'unit_price', 'discount']


class PaymentSerializer(serializers.ModelSerializer):
    """Payment serializer."""
    
    received_by_name = serializers.CharField(source='received_by.get_full_name', read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id', 'amount', 'payment_method', 'reference_number',
            'notes', 'payment_date', 'received_by', 'received_by_name', 'created_at'
        ]


class PaymentCreateSerializer(serializers.ModelSerializer):
    """Payment create serializer."""
    
    class Meta:
        model = Payment
        fields = ['amount', 'payment_method', 'reference_number', 'notes']


class InvoiceSerializer(serializers.ModelSerializer):
    """Invoice serializer."""
    
    class Meta:
        model = Invoice
        fields = [
            'id', 'invoice_number', 'status', 'issue_date',
            'due_date', 'notes', 'terms', 'created_at'
        ]


class SaleListSerializer(serializers.ModelSerializer):
    """Sale list serializer."""
    
    customer_name = serializers.CharField(source='customer.get_full_name', read_only=True)
    item_count = serializers.IntegerField(source='items.count', read_only=True)
    
    class Meta:
        model = Sale
        fields = [
            'id', 'order_number', 'customer_name', 'status', 'payment_status',
            'payment_method', 'total_amount', 'amount_paid', 'amount_due',
            'profit', 'item_count', 'order_date', 'created_at'
        ]


class SaleDetailSerializer(serializers.ModelSerializer):
    """Sale detail serializer."""
    
    items = SaleItemSerializer(many=True, read_only=True)
    payments = PaymentSerializer(many=True, read_only=True)
    invoice = InvoiceSerializer(read_only=True)
    customer = CustomerSerializer(read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = Sale
        fields = [
            'id', 'order_number', 'customer', 'status', 'payment_status',
            'payment_method', 'subtotal', 'tax_amount', 'discount_amount',
            'shipping_cost', 'total_amount', 'total_cost', 'profit',
            'amount_paid', 'amount_due', 'order_date', 'due_date',
            'completed_at', 'delivery_address', 'delivery_notes',
            'customer_notes', 'staff_notes', 'items', 'payments',
            'invoice', 'created_by', 'created_by_name', 'created_at', 'updated_at'
        ]


class SaleCreateSerializer(serializers.ModelSerializer):
    """Sale create serializer."""
    
    items = SaleItemCreateSerializer(many=True)
    
    class Meta:
        model = Sale
        fields = [
            'customer', 'payment_method', 'tax_amount', 'discount_amount',
            'shipping_cost', 'delivery_address', 'delivery_notes',
            'customer_notes', 'staff_notes', 'items'
        ]
    
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        sale = Sale.objects.create(**validated_data)
        
        for item_data in items_data:
            product = item_data.get('product')
            SaleItem.objects.create(
                sale=sale,
                product=product,
                product_name=product.name if product else 'Unknown',
                product_sku=product.sku if product else '',
                quantity=item_data['quantity'],
                unit_price=item_data['unit_price'],
                unit_cost=product.cost_price if product else 0,
                discount=item_data.get('discount', 0)
            )
            
            # Update product quantity
            if product:
                product.quantity -= item_data['quantity']
                product.save()
        
        # Recalculate totals
        sale.save()
        
        return sale


class SaleUpdateSerializer(serializers.ModelSerializer):
    """Sale update serializer."""
    
    class Meta:
        model = Sale
        fields = [
            'status', 'payment_method', 'tax_amount', 'discount_amount',
            'shipping_cost', 'delivery_address', 'delivery_notes',
            'customer_notes', 'staff_notes'
        ]


class SaleStatusUpdateSerializer(serializers.Serializer):
    """Sale status update serializer."""
    
    status = serializers.ChoiceField(choices=Sale.STATUS_CHOICES)
    notes = serializers.CharField(required=False, allow_blank=True)


class SalesStatsSerializer(serializers.Serializer):
    """Sales stats serializer."""
    
    total_sales = serializers.IntegerField()
    total_revenue = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_profit = serializers.DecimalField(max_digits=15, decimal_places=2)
    average_order_value = serializers.DecimalField(max_digits=12, decimal_places=2)
    pending_orders = serializers.IntegerField()
    completed_orders = serializers.IntegerField()
