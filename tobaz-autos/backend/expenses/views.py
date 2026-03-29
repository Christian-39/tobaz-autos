"""
Views for Expenses app.
"""
from rest_framework import generics, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q, Sum
from django.utils import timezone
from datetime import datetime
from django_filters.rest_framework import DjangoFilterBackend
from .models import ExpenseCategory, Expense, RecurringExpense, Budget
from .serializers import (
    ExpenseCategorySerializer, ExpenseCategoryCreateSerializer,
    ExpenseListSerializer, ExpenseDetailSerializer, ExpenseCreateSerializer,
    ExpenseUpdateSerializer, ExpenseApprovalSerializer,
    RecurringExpenseSerializer, RecurringExpenseCreateSerializer,
    BudgetSerializer, BudgetCreateSerializer
)
from core.utils import log_activity, upload_to_backblaze


class ExpenseCategoryListView(generics.ListCreateAPIView):
    """List and create expense categories."""
    
    queryset = ExpenseCategory.objects.filter(is_active=True)
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ExpenseCategoryCreateSerializer
        return ExpenseCategorySerializer
    
    def perform_create(self, serializer):
        category = serializer.save()
        log_activity(
            self.request.user, 'create', 'ExpenseCategory', str(category.id),
            f'Created expense category {category.name}', self.request
        )


class ExpenseCategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete an expense category."""
    
    queryset = ExpenseCategory.objects.all()
    serializer_class = ExpenseCategorySerializer
    lookup_field = 'id'
    
    def perform_update(self, serializer):
        category = serializer.save()
        log_activity(
            self.request.user, 'update', 'ExpenseCategory', str(category.id),
            f'Updated expense category {category.name}', self.request
        )
    
    def perform_destroy(self, instance):
        log_activity(
            self.request.user, 'delete', 'ExpenseCategory', str(instance.id),
            f'Deleted expense category {instance.name}', self.request
        )
        instance.delete()


class ExpenseListView(generics.ListCreateAPIView):
    """List and create expenses."""
    
    queryset = Expense.objects.all()
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    search_fields = ['title', 'description', 'reference_number', 'expense_number']
    filterset_fields = ['category', 'status', 'payment_method']
    ordering_fields = ['date', 'amount', 'created_at']
    ordering = ['-date']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ExpenseCreateSerializer
        return ExpenseListSerializer
    
    def get_queryset(self):
        queryset = Expense.objects.all()
        
        # Date range filter
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        
        return queryset
    
    def perform_create(self, serializer):
        expense = serializer.save(created_by=self.request.user)
        log_activity(
            self.request.user, 'create', 'Expense', str(expense.id),
            f'Created expense {expense.expense_number}', self.request
        )


class ExpenseDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete an expense."""
    
    queryset = Expense.objects.all()
    lookup_field = 'id'
    
    def get_serializer_class(self):
        if self.request.method == 'PUT' or self.request.method == 'PATCH':
            return ExpenseUpdateSerializer
        return ExpenseDetailSerializer
    
    def perform_update(self, serializer):
        expense = serializer.save()
        log_activity(
            self.request.user, 'update', 'Expense', str(expense.id),
            f'Updated expense {expense.expense_number}', self.request
        )
    
    def perform_destroy(self, instance):
        log_activity(
            self.request.user, 'delete', 'Expense', str(instance.id),
            f'Deleted expense {instance.expense_number}', self.request
        )
        instance.delete()


class ExpenseApprovalView(APIView):
    """Approve, reject or pay expense."""
    
    def post(self, request, pk):
        try:
            expense = Expense.objects.get(id=pk)
        except Expense.DoesNotExist:
            return Response(
                {'error': 'Expense not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = ExpenseApprovalSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        action = serializer.validated_data['action']
        reason = serializer.validated_data.get('reason', '')
        
        if action == 'approve':
            expense.approve(request.user)
            log_activity(
                request.user, 'update', 'Expense', str(expense.id),
                f'Approved expense {expense.expense_number}', request
            )
            message = 'Expense approved successfully'
        
        elif action == 'reject':
            expense.reject(request.user, reason)
            log_activity(
                request.user, 'update', 'Expense', str(expense.id),
                f'Rejected expense {expense.expense_number}', request
            )
            message = 'Expense rejected successfully'
        
        elif action == 'pay':
            expense.mark_as_paid()
            log_activity(
                request.user, 'update', 'Expense', str(expense.id),
                f'Marked expense {expense.expense_number} as paid', request
            )
            message = 'Expense marked as paid'
        
        return Response({'message': message, 'status': expense.status})


class ExpenseReceiptUploadView(APIView):
    """Upload expense receipt."""
    
    def post(self, request, pk):
        try:
            expense = Expense.objects.get(id=pk)
        except Expense.DoesNotExist:
            return Response(
                {'error': 'Expense not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        receipt_type = request.data.get('receipt_type', 'image')
        if 'receipt' not in request.FILES:
            return Response(
                {'error': 'No receipt provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        receipt = request.FILES['receipt']
        receipt_url = upload_to_backblaze(receipt, f'expenses/{expense.id}/receipts')
        
        if not receipt_url:
            return Response(
                {'error': 'Failed to upload receipt'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        if receipt_type == 'image':
            expense.receipt_image = receipt_url
        else:
            expense.receipt_file = receipt_url
        
        expense.save()
        
        log_activity(
            request.user, 'update', 'Expense', str(expense.id),
            f'Uploaded receipt for {expense.expense_number}', request
        )
        
        return Response({'receipt_url': receipt_url})


class RecurringExpenseListView(generics.ListCreateAPIView):
    """List and create recurring expenses."""
    
    queryset = RecurringExpense.objects.all()
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['title', 'description']
    filterset_fields = ['category', 'frequency', 'status']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return RecurringExpenseCreateSerializer
        return RecurringExpenseSerializer
    
    def perform_create(self, serializer):
        recurring = serializer.save(created_by=self.request.user)
        log_activity(
            self.request.user, 'create', 'RecurringExpense', str(recurring.id),
            f'Created recurring expense {recurring.title}', self.request
        )


class RecurringExpenseDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a recurring expense."""
    
    queryset = RecurringExpense.objects.all()
    serializer_class = RecurringExpenseSerializer
    lookup_field = 'id'
    
    def perform_update(self, serializer):
        recurring = serializer.save()
        log_activity(
            self.request.user, 'update', 'RecurringExpense', str(recurring.id),
            f'Updated recurring expense {recurring.title}', self.request
        )
    
    def perform_destroy(self, instance):
        log_activity(
            self.request.user, 'delete', 'RecurringExpense', str(instance.id),
            f'Deleted recurring expense {instance.title}', self.request
        )
        instance.delete()


class GenerateRecurringExpenseView(APIView):
    """Generate expense from recurring expense."""
    
    def post(self, request, pk):
        try:
            recurring = RecurringExpense.objects.get(id=pk)
        except RecurringExpense.DoesNotExist:
            return Response(
                {'error': 'Recurring expense not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        expense = recurring.generate_next_expense()
        
        if expense:
            log_activity(
                request.user, 'create', 'Expense', str(expense.id),
                f'Generated expense from recurring {recurring.title}', request
            )
            return Response({
                'message': 'Expense generated successfully',
                'expense_id': str(expense.id),
                'expense_number': expense.expense_number
            })
        
        return Response(
            {'error': 'Could not generate expense'},
            status=status.HTTP_400_BAD_REQUEST
        )


class BudgetListView(generics.ListCreateAPIView):
    """List and create budgets."""
    
    queryset = Budget.objects.filter(is_active=True)
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['title']
    filterset_fields = ['category']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return BudgetCreateSerializer
        return BudgetSerializer
    
    def perform_create(self, serializer):
        budget = serializer.save(created_by=self.request.user)
        log_activity(
            self.request.user, 'create', 'Budget', str(budget.id),
            f'Created budget {budget.title}', self.request
        )


class BudgetDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a budget."""
    
    queryset = Budget.objects.all()
    serializer_class = BudgetSerializer
    lookup_field = 'id'
    
    def perform_update(self, serializer):
        budget = serializer.save()
        log_activity(
            self.request.user, 'update', 'Budget', str(budget.id),
            f'Updated budget {budget.title}', self.request
        )
    
    def perform_destroy(self, instance):
        log_activity(
            self.request.user, 'delete', 'Budget', str(instance.id),
            f'Deleted budget {instance.title}', self.request
        )
        instance.delete()


class ExpenseStatsView(APIView):
    """Get expense statistics."""
    
    def get(self, request):
        today = timezone.now().date()
        start_of_month = today.replace(day=1)
        start_of_year = today.replace(month=1, day=1)
        
        # Overall stats
        total_expenses = Expense.objects.count()
        total_amount = Expense.objects.filter(
            status='paid'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        pending_amount = Expense.objects.filter(
            status='pending'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        paid_amount = Expense.objects.filter(
            status='paid',
            date__month=today.month,
            date__year=today.year
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # This month
        this_month = Expense.objects.filter(
            date__gte=start_of_month
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # This year
        this_year = Expense.objects.filter(
            date__gte=start_of_year
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # By category
        by_category = Expense.objects.filter(
            status='paid',
            date__month=today.month,
            date__year=today.year
        ).values('category__name', 'category__color').annotate(
            total=Sum('amount')
        ).order_by('-total')
        
        return Response({
            'total_expenses': total_expenses,
            'total_amount': total_amount,
            'pending_amount': pending_amount,
            'paid_amount': paid_amount,
            'this_month': this_month,
            'this_year': this_year,
            'by_category': list(by_category),
        })


class ExpenseChartView(APIView):
    """Get expense data for charts."""
    
    def get(self, request):
        period = request.query_params.get('period', 'month')
        today = timezone.now().date()
        
        if period == 'week':
            from datetime import timedelta
            start_date = today - timedelta(days=7)
        elif period == 'month':
            from datetime import timedelta
            start_date = today - timedelta(days=30)
        else:  # year
            from datetime import timedelta
            start_date = today - timedelta(days=365)
        
        expenses = Expense.objects.filter(
            date__gte=start_date,
            status='paid'
        ).values('date').annotate(
            total=Sum('amount')
        ).order_by('date')
        
        labels = []
        data = []
        
        for expense in expenses:
            labels.append(expense['date'].strftime('%Y-%m-%d'))
            data.append(float(expense['total']))
        
        return Response({
            'labels': labels,
            'data': data,
        })
