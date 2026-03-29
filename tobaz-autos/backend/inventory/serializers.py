"""
Serializers for Inventory app.
"""
from rest_framework import serializers
from .models import Category, Product, InventoryTransaction, Supplier


class CategorySerializer(serializers.ModelSerializer):
    """Category serializer."""
    
    product_count = serializers.IntegerField(source='products.count', read_only=True)
    
    class Meta:
        model = Category
        fields = [
            'id', 'name', 'slug', 'category_type', 'description',
            'icon', 'color', 'is_active', 'product_count', 'created_at'
        ]


class CategoryCreateSerializer(serializers.ModelSerializer):
    """Category create serializer."""
    
    class Meta:
        model = Category
        fields = ['name', 'category_type', 'description', 'icon', 'color']


class ProductListSerializer(serializers.ModelSerializer):
    """Product list serializer."""
    
    category_name = serializers.CharField(source='category.name', read_only=True)
    stock_status = serializers.CharField(read_only=True)
    profit_margin = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'sku', 'name', 'slug', 'category', 'category_name',
            'cost_price', 'selling_price', 'quantity', 'stock_status',
            'profit_margin', 'condition', 'featured_image', 'status',
            'is_featured', 'created_at'
        ]


class ProductDetailSerializer(serializers.ModelSerializer):
    """Product detail serializer."""
    
    category_name = serializers.CharField(source='category.name', read_only=True)
    stock_status = serializers.CharField(read_only=True)
    profit_margin = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)
    inventory_value = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'sku', 'name', 'slug', 'description', 'category', 'category_name',
            'cost_price', 'selling_price', 'quantity', 'reorder_level',
            'reorder_quantity', 'stock_status', 'profit_margin', 'inventory_value',
            'brand', 'model', 'year', 'condition', 'mileage', 'fuel_type',
            'transmission', 'color', 'vin', 'featured_image', 'images',
            'meta_title', 'meta_description', 'meta_keywords',
            'status', 'is_featured', 'created_by', 'created_by_name',
            'created_at', 'updated_at'
        ]


class ProductCreateSerializer(serializers.ModelSerializer):
    """Product create serializer."""
    
    class Meta:
        model = Product
        fields = [
            'name', 'description', 'category', 'cost_price', 'selling_price',
            'quantity', 'reorder_level', 'reorder_quantity', 'brand', 'model',
            'year', 'condition', 'mileage', 'fuel_type', 'transmission',
            'color', 'vin', 'featured_image', 'images', 'meta_title',
            'meta_description', 'meta_keywords', 'status', 'is_featured'
        ]


class ProductUpdateSerializer(serializers.ModelSerializer):
    """Product update serializer."""
    
    class Meta:
        model = Product
        fields = [
            'name', 'description', 'category', 'cost_price', 'selling_price',
            'reorder_level', 'reorder_quantity', 'brand', 'model', 'year',
            'condition', 'mileage', 'fuel_type', 'transmission', 'color',
            'vin', 'featured_image', 'images', 'meta_title', 'meta_description',
            'meta_keywords', 'status', 'is_featured'
        ]


class InventoryTransactionSerializer(serializers.ModelSerializer):
    """Inventory transaction serializer."""
    
    product_name = serializers.CharField(source='product.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = InventoryTransaction
        fields = [
            'id', 'product', 'product_name', 'transaction_type', 'quantity',
            'previous_quantity', 'new_quantity', 'reference', 'notes',
            'created_by', 'created_by_name', 'created_at'
        ]


class StockAdjustmentSerializer(serializers.Serializer):
    """Stock adjustment serializer."""
    
    quantity = serializers.IntegerField(required=True)
    reason = serializers.CharField(required=True)
    reference = serializers.CharField(required=False, allow_blank=True)


class SupplierSerializer(serializers.ModelSerializer):
    """Supplier serializer."""
    
    class Meta:
        model = Supplier
        fields = [
            'id', 'name', 'contact_person', 'email', 'phone', 'address',
            'country', 'website', 'notes', 'is_active', 'created_at'
        ]
