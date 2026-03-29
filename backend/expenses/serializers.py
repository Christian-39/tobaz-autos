"""
Serializers for Expenses app.
"""
from rest_framework import serializers
from .models import ExpenseCategory, Expense, RecurringExpense, Budget


class ExpenseCategorySerializer(serializers.ModelSerializer):
    """Expense category serializer."""
    
    expense_count = serializers.IntegerField(source='expenses.count', read_only=True)
    total_spent = serializers.SerializerMethodField()
    
    class Meta:
        model = ExpenseCategory
        fields = [
            'id', 'name', 'description', 'color', 'icon',
            'is_active', 'expense_count', 'total_spent', 'created_at'
        ]
    
    def get_total_spent(self, obj):
        from django.db.models import Sum
        return obj.expenses.filter(status='paid').aggregate(
            total=Sum('amount')
        )['total'] or 0


class ExpenseCategoryCreateSerializer(serializers.ModelSerializer):
    """Expense category create serializer."""
    
    class Meta:
        model = ExpenseCategory
        fields = ['name', 'description', 'color', 'icon']


class ExpenseListSerializer(serializers.ModelSerializer):
    """Expense list serializer."""
    
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_color = serializers.CharField(source='category.color', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = Expense
        fields = [
            'id', 'expense_number', 'title', 'category', 'category_name',
            'category_color', 'amount', 'date', 'payment_method',
            'status', 'created_by_name', 'created_at'
        ]


class ExpenseDetailSerializer(serializers.ModelSerializer):
    """Expense detail serializer."""
    
    category = ExpenseCategorySerializer(read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.get_full_name', read_only=True)
    
    class Meta:
        model = Expense
        fields = [
            'id', 'expense_number', 'category', 'title', 'description',
            'amount', 'date', 'payment_method', 'reference_number',
            'receipt_image', 'receipt_file', 'status', 'approved_by',
            'approved_by_name', 'approved_at', 'rejection_reason',
            'created_by', 'created_by_name', 'created_at', 'updated_at'
        ]


class ExpenseCreateSerializer(serializers.ModelSerializer):
    """Expense create serializer."""
    
    class Meta:
        model = Expense
        fields = [
            'category', 'title', 'description', 'amount', 'date',
            'payment_method', 'reference_number'
        ]


class ExpenseUpdateSerializer(serializers.ModelSerializer):
    """Expense update serializer."""
    
    class Meta:
        model = Expense
        fields = [
            'category', 'title', 'description', 'amount', 'date',
            'payment_method', 'reference_number'
        ]


class ExpenseApprovalSerializer(serializers.Serializer):
    """Expense approval serializer."""
    
    action = serializers.ChoiceField(choices=['approve', 'reject', 'pay'])
    reason = serializers.CharField(required=False, allow_blank=True)


class RecurringExpenseSerializer(serializers.ModelSerializer):
    """Recurring expense serializer."""
    
    category_name = serializers.CharField(source='category.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = RecurringExpense
        fields = [
            'id', 'category', 'category_name', 'title', 'description',
            'amount', 'frequency', 'start_date', 'end_date',
            'next_due_date', 'status', 'created_by_name', 'created_at'
        ]


class RecurringExpenseCreateSerializer(serializers.ModelSerializer):
    """Recurring expense create serializer."""
    
    class Meta:
        model = RecurringExpense
        fields = [
            'category', 'title', 'description', 'amount', 'frequency',
            'start_date', 'end_date', 'next_due_date'
        ]


class BudgetSerializer(serializers.ModelSerializer):
    """Budget serializer."""
    
    category_name = serializers.CharField(source='category.name', read_only=True)
    spent = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    remaining = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    percentage_used = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)
    is_alert = serializers.BooleanField(read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = Budget
        fields = [
            'id', 'category', 'category_name', 'title', 'amount',
            'start_date', 'end_date', 'spent', 'remaining',
            'percentage_used', 'alert_threshold', 'is_alert',
            'is_active', 'created_by_name', 'created_at'
        ]


class BudgetCreateSerializer(serializers.ModelSerializer):
    """Budget create serializer."""
    
    class Meta:
        model = Budget
        fields = [
            'category', 'title', 'amount', 'start_date',
            'end_date', 'alert_threshold'
        ]


class ExpenseStatsSerializer(serializers.Serializer):
    """Expense stats serializer."""
    
    total_expenses = serializers.IntegerField()
    total_amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    pending_amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    paid_amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    this_month = serializers.DecimalField(max_digits=15, decimal_places=2)
    this_year = serializers.DecimalField(max_digits=15, decimal_places=2)
