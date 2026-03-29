"""
Views for Sales app.
"""
from rest_framework import generics, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q, Sum, Count, Avg, F
from django.utils import timezone
from datetime import datetime, timedelta
from django_filters.rest_framework import DjangoFilterBackend
from .models import Customer, Sale, SaleItem, Payment, Invoice
from .serializers import (
    CustomerSerializer, CustomerCreateSerializer, SaleListSerializer,
    SaleDetailSerializer, SaleCreateSerializer, SaleUpdateSerializer,
    SaleStatusUpdateSerializer, PaymentSerializer, PaymentCreateSerializer,
    InvoiceSerializer, SalesStatsSerializer
)
from core.utils import log_activity
from inventory.models import InventoryTransaction


class CustomerListView(generics.ListCreateAPIView):
    """List and create customers."""
    
    queryset = Customer.objects.filter(is_active=True)
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    search_fields = ['first_name', 'last_name', 'email', 'phone', 'company_name']
    filterset_fields = ['customer_type']
    ordering_fields = ['created_at', 'first_name']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CustomerCreateSerializer
        return CustomerSerializer
    
    def perform_create(self, serializer):
        customer = serializer.save()
        log_activity(
            self.request.user, 'create', 'Customer', str(customer.id),
            f'Created customer {customer.get_full_name()}', self.request
        )


class CustomerDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a customer."""
    
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    lookup_field = 'id'
    
    def get_serializer_class(self):
        if self.request.method == 'PUT' or self.request.method == 'PATCH':
            return CustomerCreateSerializer
        return CustomerSerializer
    
    def perform_update(self, serializer):
        customer = serializer.save()
        log_activity(
            self.request.user, 'update', 'Customer', str(customer.id),
            f'Updated customer {customer.get_full_name()}', self.request
        )
    
    def perform_destroy(self, instance):
        log_activity(
            self.request.user, 'delete', 'Customer', str(instance.id),
            f'Deleted customer {instance.get_full_name()}', self.request
        )
        instance.delete()


class SaleListView(generics.ListCreateAPIView):
    """List and create sales."""
    
    queryset = Sale.objects.all()
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    search_fields = ['order_number', 'customer__first_name', 'customer__last_name', 'customer__phone']
    filterset_fields = ['status', 'payment_status', 'payment_method']
    ordering_fields = ['created_at', 'total_amount', 'order_date']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return SaleCreateSerializer
        return SaleListSerializer
    
    def get_queryset(self):
        queryset = Sale.objects.all()
        
        # Date range filter
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(created_at__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__date__lte=end_date)
        
        return queryset
    
    def perform_create(self, serializer):
        sale = serializer.save(created_by=self.request.user)
        log_activity(
            self.request.user, 'create', 'Sale', str(sale.id),
            f'Created sale {sale.order_number}', self.request
        )


class SaleDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a sale."""
    
    queryset = Sale.objects.all()
    lookup_field = 'id'
    
    def get_serializer_class(self):
        if self.request.method == 'PUT' or self.request.method == 'PATCH':
            return SaleUpdateSerializer
        return SaleDetailSerializer
    
    def perform_update(self, serializer):
        sale = serializer.save()
        log_activity(
            self.request.user, 'update', 'Sale', str(sale.id),
            f'Updated sale {sale.order_number}', self.request
        )
    
    def perform_destroy(self, instance):
        # Restore product quantities
        for item in instance.items.all():
            if item.product:
                item.product.quantity += item.quantity
                item.product.save()
        
        log_activity(
            self.request.user, 'delete', 'Sale', str(instance.id),
            f'Deleted sale {instance.order_number}', self.request
        )
        instance.delete()


class SaleStatusUpdateView(APIView):
    """Update sale status."""
    
    def post(self, request, pk):
        try:
            sale = Sale.objects.get(id=pk)
        except Sale.DoesNotExist:
            return Response(
                {'error': 'Sale not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = SaleStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        old_status = sale.status
        new_status = serializer.validated_data['status']
        
        sale.status = new_status
        
        if new_status == 'completed':
            sale.completed_at = timezone.now()
            sale.payment_status = 'paid'
        
        sale.save()
        
        log_activity(
            request.user, 'update', 'Sale', str(sale.id),
            f'Updated sale status: {old_status} -> {new_status}', request
        )
        
        return Response({
            'message': 'Status updated successfully',
            'old_status': old_status,
            'new_status': new_status
        })


class AddPaymentView(APIView):
    """Add payment to sale."""
    
    def post(self, request, pk):
        try:
            sale = Sale.objects.get(id=pk)
        except Sale.DoesNotExist:
            return Response(
                {'error': 'Sale not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = PaymentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        payment = Payment.objects.create(
            sale=sale,
            **serializer.validated_data,
            received_by=request.user
        )
        
        log_activity(
            request.user, 'create', 'Payment', str(payment.id),
            f'Added payment of ₦{payment.amount} to {sale.order_number}', request
        )
        
        return Response(PaymentSerializer(payment).data, status=status.HTTP_201_CREATED)


class CreateInvoiceView(APIView):
    """Create invoice for sale."""
    
    def post(self, request, pk):
        try:
            sale = Sale.objects.get(id=pk)
        except Sale.DoesNotExist:
            return Response(
                {'error': 'Sale not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if hasattr(sale, 'invoice'):
            return Response(
                {'error': 'Invoice already exists for this sale'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        due_date = request.data.get('due_date')
        if due_date:
            from datetime import datetime
            due_date = datetime.strptime(due_date, '%Y-%m-%d').date()
        else:
            from datetime import timedelta
            due_date = timezone.now().date() + timedelta(days=30)
        
        invoice = Invoice.objects.create(
            sale=sale,
            due_date=due_date,
            notes=request.data.get('notes', ''),
            terms=request.data.get('terms', '')
        )
        
        log_activity(
            request.user, 'create', 'Invoice', str(invoice.id),
            f'Created invoice {invoice.invoice_number} for {sale.order_number}', request
        )
        
        return Response(InvoiceSerializer(invoice).data, status=status.HTTP_201_CREATED)


class SalesStatsView(APIView):
    """Get sales statistics."""
    
    def get(self, request):
        today = timezone.now().date()
        start_of_month = today.replace(day=1)
        start_of_year = today.replace(month=1, day=1)
        
        # Overall stats
        total_sales = Sale.objects.count()
        total_revenue = Sale.objects.filter(
            status='completed'
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        
        total_profit = Sale.objects.filter(
            status='completed'
        ).aggregate(total=Sum('profit'))['total'] or 0
        
        avg_order = Sale.objects.filter(
            status='completed'
        ).aggregate(avg=Avg('total_amount'))['avg'] or 0
        
        # Monthly stats
        month_sales = Sale.objects.filter(
            created_at__date__gte=start_of_month
        ).aggregate(
            total=Sum('total_amount'),
            profit=Sum('profit'),
            count=Count('id')
        )
        
        # Status counts
        pending_orders = Sale.objects.filter(status='pending').count()
        completed_orders = Sale.objects.filter(status='completed').count()
        
        # Payment status
        unpaid_amount = Sale.objects.filter(
            payment_status__in=['pending', 'partial']
        ).aggregate(total=Sum('amount_due'))['total'] or 0
        
        return Response({
            'overall': {
                'total_sales': total_sales,
                'total_revenue': total_revenue,
                'total_profit': total_profit,
                'average_order_value': avg_order,
            },
            'monthly': {
                'sales': month_sales['count'] or 0,
                'revenue': month_sales['total'] or 0,
                'profit': month_sales['profit'] or 0,
            },
            'orders': {
                'pending': pending_orders,
                'completed': completed_orders,
            },
            'payments': {
                'unpaid_amount': unpaid_amount,
            }
        })


class SalesChartView(APIView):
    """Get sales data for charts."""
    
    def get(self, request):
        period = request.query_params.get('period', 'month')
        today = timezone.now().date()
        
        if period == 'week':
            start_date = today - timedelta(days=7)
        elif period == 'month':
            start_date = today - timedelta(days=30)
        else:  # year
            start_date = today - timedelta(days=365)
        
        sales = Sale.objects.filter(
            created_at__date__gte=start_date,
            status='completed'
        ).values('created_at__date').annotate(
            revenue=Sum('total_amount'),
            profit=Sum('profit'),
            count=Count('id')
        ).order_by('created_at__date')
        
        labels = []
        revenue_data = []
        profit_data = []
        count_data = []
        
        for sale in sales:
            labels.append(sale['created_at__date'].strftime('%Y-%m-%d'))
            revenue_data.append(float(sale['revenue']))
            profit_data.append(float(sale['profit']))
            count_data.append(sale['count'])
        
        return Response({
            'labels': labels,
            'revenue': revenue_data,
            'profit': profit_data,
            'count': count_data,
        })


class TopCustomersView(APIView):
    """Get top customers by spending."""
    
    def get(self, request):
        limit = int(request.query_params.get('limit', 10))
        
        customers = Customer.objects.filter(
            sales__status='completed'
        ).annotate(
            total_spent=Sum('sales__total_amount'),
            order_count=Count('sales')
        ).order_by('-total_spent')[:limit]
        
        data = [{
            'id': str(c.id),
            'name': c.get_full_name(),
            'email': c.email,
            'phone': c.phone,
            'total_spent': c.total_spent or 0,
            'order_count': c.order_count or 0,
        } for c in customers]
        
        return Response(data)


class TopProductsView(APIView):
    """Get top selling products."""
    
    def get(self, request):
        limit = int(request.query_params.get('limit', 10))
        
        products = SaleItem.objects.filter(
            sale__status='completed'
        ).values(
            'product', 'product_name', 'product_sku'
        ).annotate(
            total_quantity=Sum('quantity'),
            total_revenue=Sum('total_price')
        ).order_by('-total_quantity')[:limit]
        
        return Response(products)
