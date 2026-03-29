"""
Dashboard views for statistics and charts.
"""
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Sum, Count, Avg, F, Q
from django.utils import timezone
from datetime import datetime, timedelta
from inventory.models import Product, Category
from sales.models import Sale, SaleItem
from shipments.models import Shipment
from expenses.models import Expense


class DashboardStatsView(APIView):
    """Get dashboard statistics."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        today = timezone.now().date()
        start_of_month = today.replace(day=1)
        start_of_year = today.replace(month=1, day=1)
        
        # Product stats
        total_products = Product.objects.count()
        low_stock_products = Product.objects.filter(quantity__lte=F('reorder_level')).count()
        out_of_stock_products = Product.objects.filter(quantity=0).count()
        
        # Sales stats
        today_sales = Sale.objects.filter(
            created_at__date=today,
            status='completed'
        ).aggregate(
            total=Sum('total_amount'),
            count=Count('id')
        )
        
        month_sales = Sale.objects.filter(
            created_at__date__gte=start_of_month,
            status='completed'
        ).aggregate(
            total=Sum('total_amount'),
            count=Count('id')
        )
        
        year_sales = Sale.objects.filter(
            created_at__date__gte=start_of_year,
            status='completed'
        ).aggregate(
            total=Sum('total_amount'),
            count=Count('id')
        )
        
        # Profit calculation
        today_profit = Sale.objects.filter(
            created_at__date=today,
            status='completed'
        ).aggregate(
            profit=Sum(F('total_amount') - F('total_cost'))
        )['profit'] or 0
        
        month_profit = Sale.objects.filter(
            created_at__date__gte=start_of_month,
            status='completed'
        ).aggregate(
            profit=Sum(F('total_amount') - F('total_cost'))
        )['profit'] or 0
        
        # Shipment stats
        pending_shipments = Shipment.objects.filter(status='in_transit').count()
        received_this_month = Shipment.objects.filter(
            status='received',
            received_at__date__gte=start_of_month
        ).count()
        
        # Expense stats
        month_expenses = Expense.objects.filter(
            date__gte=start_of_month
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # Inventory value
        inventory_value = Product.objects.aggregate(
            value=Sum(F('quantity') * F('cost_price'))
        )['value'] or 0
        
        # Category distribution
        categories = Category.objects.annotate(
            product_count=Count('products')
        ).values('name', 'product_count')
        
        return Response({
            'products': {
                'total': total_products,
                'low_stock': low_stock_products,
                'out_of_stock': out_of_stock_products,
            },
            'sales': {
                'today': {
                    'amount': today_sales['total'] or 0,
                    'count': today_sales['count'] or 0,
                },
                'month': {
                    'amount': month_sales['total'] or 0,
                    'count': month_sales['count'] or 0,
                },
                'year': {
                    'amount': year_sales['total'] or 0,
                    'count': year_sales['count'] or 0,
                },
            },
            'profit': {
                'today': today_profit,
                'month': month_profit,
            },
            'shipments': {
                'pending': pending_shipments,
                'received_this_month': received_this_month,
            },
            'expenses': {
                'month': month_expenses,
            },
            'inventory_value': inventory_value,
            'categories': list(categories),
        })


class SalesChartView(APIView):
    """Get sales data for charts."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        period = request.query_params.get('period', 'month')  # week, month, year
        
        today = timezone.now().date()
        
        if period == 'week':
            start_date = today - timedelta(days=7)
            date_format = '%Y-%m-%d'
        elif period == 'month':
            start_date = today - timedelta(days=30)
            date_format = '%Y-%m-%d'
        else:  # year
            start_date = today - timedelta(days=365)
            date_format = '%Y-%m'
        
        sales = Sale.objects.filter(
            created_at__date__gte=start_date,
            status='completed'
        ).values('created_at__date').annotate(
            total=Sum('total_amount'),
            count=Count('id')
        ).order_by('created_at__date')
        
        # Format data for chart
        labels = []
        data = []
        
        for sale in sales:
            date_str = sale['created_at__date'].strftime(date_format)
            labels.append(date_str)
            data.append(float(sale['total']))
        
        return Response({
            'labels': labels,
            'data': data,
        })


class InventoryChartView(APIView):
    """Get inventory data for charts."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        # Products by category
        categories = Category.objects.annotate(
            product_count=Count('products'),
            total_value=Sum(F('products__quantity') * F('products__cost_price'))
        ).values('name', 'product_count', 'total_value')
        
        # Stock status
        stock_status = {
            'in_stock': Product.objects.filter(quantity__gt=F('reorder_level')).count(),
            'low_stock': Product.objects.filter(
                quantity__gt=0,
                quantity__lte=F('reorder_level')
            ).count(),
            'out_of_stock': Product.objects.filter(quantity=0).count(),
        }
        
        # Top products by quantity
        top_products = Product.objects.order_by('-quantity')[:10].values(
            'name', 'quantity', 'sku'
        )
        
        return Response({
            'categories': list(categories),
            'stock_status': stock_status,
            'top_products': list(top_products),
        })
