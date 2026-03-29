"""
Views for Inventory app.
"""
from rest_framework import generics, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q, F
from django_filters.rest_framework import DjangoFilterBackend
from .models import Category, Product, InventoryTransaction, Supplier
from rest_framework.parsers import MultiPartParser, FormParser
from .serializers import (
    CategorySerializer, CategoryCreateSerializer, ProductListSerializer,
    ProductDetailSerializer, ProductCreateSerializer, ProductUpdateSerializer,
    InventoryTransactionSerializer, StockAdjustmentSerializer, SupplierSerializer
)
from core.utils import log_activity, upload_to_backblaze


class CategoryListView(generics.ListCreateAPIView):
    """List and create categories."""
    
    queryset = Category.objects.filter(is_active=True)
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['name', 'description']
    filterset_fields = ['category_type']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CategoryCreateSerializer
        return CategorySerializer
    
    def perform_create(self, serializer):
        category = serializer.save()
        log_activity(
            self.request.user, 'create', 'Category', str(category.id),
            f'Created category {category.name}', self.request
        )


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a category."""
    
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'id'
    
    def perform_update(self, serializer):
        category = serializer.save()
        log_activity(
            self.request.user, 'update', 'Category', str(category.id),
            f'Updated category {category.name}', self.request
        )
    
    def perform_destroy(self, instance):
        log_activity(
            self.request.user, 'delete', 'Category', str(instance.id),
            f'Deleted category {instance.name}', self.request
        )
        instance.delete()


class ProductListView(generics.ListCreateAPIView):
    """List and create products."""
    
    queryset = Product.objects.all()
    parser_classes = (MultiPartParser, FormParser)
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    search_fields = ['name', 'sku', 'description', 'brand', 'model']
    filterset_fields = ['category', 'status', 'condition', 'is_featured']
    ordering_fields = ['name', 'created_at', 'selling_price', 'quantity']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ProductCreateSerializer
        return ProductListSerializer
    
    def get_queryset(self):
        queryset = Product.objects.all()
        
        # Stock status filter
        stock_status = self.request.query_params.get('stock_status', '')
        if stock_status == 'low_stock':
            queryset = queryset.filter(quantity__gt=0, quantity__lte=F('reorder_level'))
        elif stock_status == 'out_of_stock':
            queryset = queryset.filter(quantity=0)
        elif stock_status == 'in_stock':
            queryset = queryset.filter(quantity__gt=F('reorder_level'))
        
        # Price range filter
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        if min_price:
            queryset = queryset.filter(selling_price__gte=min_price)
        if max_price:
            queryset = queryset.filter(selling_price__lte=max_price)
        
        return queryset
    
    def perform_create(self, serializer):
        product = serializer.save(created_by=self.request.user)
        log_activity(
            self.request.user, 'create', 'Product', str(product.id),
            f'Created product {product.name}', self.request
        )


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a product."""
    
    queryset = Product.objects.all()
    lookup_field = 'id'
    
    def get_serializer_class(self):
        if self.request.method == 'PUT' or self.request.method == 'PATCH':
            return ProductUpdateSerializer
        return ProductDetailSerializer
    
    def perform_update(self, serializer):
        product = serializer.save()
        log_activity(
            self.request.user, 'update', 'Product', str(product.id),
            f'Updated product {product.name}', self.request
        )
    
    def perform_destroy(self, instance):
        log_activity(
            self.request.user, 'delete', 'Product', str(instance.id),
            f'Deleted product {instance.name}', self.request
        )
        instance.delete()


class ProductBySlugView(generics.RetrieveAPIView):
    """Get product by slug (for SEO-friendly URLs)."""
    
    queryset = Product.objects.filter(status='active')
    serializer_class = ProductDetailSerializer
    lookup_field = 'slug'
    permission_classes = []


class ProductImageUploadView(APIView):
    """Upload product image."""
    
    def post(self, request, pk):
        try:
            product = Product.objects.get(id=pk)
        except Product.DoesNotExist:
            return Response(
                {'error': 'Product not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if 'image' not in request.FILES:
            return Response(
                {'error': 'No image provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        image = request.FILES['image']
        image_url = upload_to_backblaze(image, f'products/{product.id}')
        
        if not image_url:
            return Response(
                {'error': 'Failed to upload image'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Add to images array
        if not product.images:
            product.images = []
        product.images.append(image_url)
        product.save()
        
        log_activity(
            request.user, 'update', 'Product', str(product.id),
            f'Uploaded image for {product.name}', request
        )
        
        return Response({'image_url': image_url, 'images': product.images})


class StockAdjustmentView(APIView):
    """Adjust product stock."""
    
    def post(self, request, pk):
        try:
            product = Product.objects.get(id=pk)
        except Product.DoesNotExist:
            return Response(
                {'error': 'Product not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = StockAdjustmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        quantity = serializer.validated_data['quantity']
        reason = serializer.validated_data['reason']
        reference = serializer.validated_data.get('reference', '')
        
        previous_quantity = product.quantity
        new_quantity = max(0, previous_quantity + quantity)
        
        # Update product quantity
        product.quantity = new_quantity
        product.save()
        
        # Create transaction record
        transaction_type = 'in' if quantity > 0 else 'out'
        if quantity == 0:
            transaction_type = 'adjustment'
        
        InventoryTransaction.objects.create(
            product=product,
            transaction_type=transaction_type,
            quantity=abs(quantity),
            previous_quantity=previous_quantity,
            new_quantity=new_quantity,
            reference=reference,
            notes=reason,
            created_by=request.user
        )
        
        log_activity(
            request.user, 'update', 'Product', str(product.id),
            f'Stock adjustment for {product.name}: {previous_quantity} -> {new_quantity}',
            request
        )
        
        return Response({
            'message': 'Stock adjusted successfully',
            'previous_quantity': previous_quantity,
            'new_quantity': new_quantity
        })


class InventoryTransactionListView(generics.ListAPIView):
    """List inventory transactions."""
    
    serializer_class = InventoryTransactionSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    search_fields = ['product__name', 'reference', 'notes']
    filterset_fields = ['transaction_type', 'product']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = InventoryTransaction.objects.all()
        
        # Date range filter
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(created_at__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__date__lte=end_date)
        
        return queryset


class SupplierListView(generics.ListCreateAPIView):
    """List and create suppliers."""
    
    queryset = Supplier.objects.filter(is_active=True)
    serializer_class = SupplierSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'contact_person', 'email', 'phone']
    
    def perform_create(self, serializer):
        supplier = serializer.save()
        log_activity(
            self.request.user, 'create', 'Supplier', str(supplier.id),
            f'Created supplier {supplier.name}', self.request
        )


class SupplierDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a supplier."""
    
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    lookup_field = 'id'
    
    def perform_update(self, serializer):
        supplier = serializer.save()
        log_activity(
            self.request.user, 'update', 'Supplier', str(supplier.id),
            f'Updated supplier {supplier.name}', self.request
        )
    
    def perform_destroy(self, instance):
        log_activity(
            self.request.user, 'delete', 'Supplier', str(instance.id),
            f'Deleted supplier {instance.name}', self.request
        )
        instance.delete()


class LowStockProductsView(generics.ListAPIView):
    """Get low stock products."""
    
    serializer_class = ProductListSerializer
    
    def get_queryset(self):
        return Product.objects.filter(
            quantity__gt=0,
            quantity__lte=F('reorder_level')
        ).order_by('quantity')


class OutOfStockProductsView(generics.ListAPIView):
    """Get out of stock products."""
    
    serializer_class = ProductListSerializer
    
    def get_queryset(self):
        return Product.objects.filter(quantity=0).order_by('-updated_at')
