"""
Admin configuration for Expenses app.
"""
from django.contrib import admin
from .models import ExpenseCategory, Expense, RecurringExpense, Budget


@admin.register(ExpenseCategory)
class ExpenseCategoryAdmin(admin.ModelAdmin):
    """Expense category admin configuration."""
    
    list_display = ['name', 'expense_count', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    
    def expense_count(self, obj):
        return obj.expenses.count()


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    """Expense admin configuration."""
    
    list_display = [
        'expense_number', 'title', 'category', 'amount',
        'date', 'status', 'created_by', 'created_at'
    ]
    list_filter = ['status', 'payment_method', 'category', 'date']
    search_fields = ['expense_number', 'title', 'description', 'reference_number']
    date_hierarchy = 'date'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('expense_number', 'category', 'title', 'description')
        }),
        ('Financial', {
            'fields': ('amount', 'date', 'payment_method', 'reference_number')
        }),
        ('Receipts', {
            'fields': ('receipt_image', 'receipt_file'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Approval', {
            'fields': ('approved_by', 'approved_at', 'rejection_reason'),
            'classes': ('collapse',)
        }),
    )


@admin.register(RecurringExpense)
class RecurringExpenseAdmin(admin.ModelAdmin):
    """Recurring expense admin configuration."""
    
    list_display = [
        'title', 'category', 'amount', 'frequency',
        'next_due_date', 'status'
    ]
    list_filter = ['frequency', 'status', 'category']
    search_fields = ['title', 'description']


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    """Budget admin configuration."""
    
    list_display = [
        'title', 'category', 'amount', 'spent',
        'remaining', 'percentage_used', 'is_alert', 'is_active'
    ]
    list_filter = ['is_active', 'category']
    search_fields = ['title']
    
    readonly_fields = ['spent', 'remaining', 'percentage_used', 'is_alert']
