"""
Expense models for Tobaz Autos.
"""
import uuid
from django.db import models
from django.utils import timezone


class ExpenseCategory(models.Model):
    """Expense category model."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    color = models.CharField(max_length=7, default='#6366f1')
    icon = models.CharField(max_length=50, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'expense_categories'
        verbose_name_plural = 'Expense Categories'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Expense(models.Model):
    """Expense model."""
    
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('transfer', 'Bank Transfer'),
        ('card', 'Card'),
        ('check', 'Check'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('paid', 'Paid'),
        ('rejected', 'Rejected'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    expense_number = models.CharField(max_length=50, unique=True, blank=True)
    category = models.ForeignKey(
        ExpenseCategory, on_delete=models.SET_NULL, null=True, related_name='expenses'
    )
    
    # Expense details
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField(default=timezone.now)
    
    # Payment
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='cash')
    reference_number = models.CharField(max_length=100, blank=True, null=True)
    
    # Receipt
    receipt_image = models.URLField(blank=True, null=True)
    receipt_file = models.URLField(blank=True, null=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Approval
    approved_by = models.ForeignKey(
        'core.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='expenses_approved'
    )
    approved_at = models.DateTimeField(blank=True, null=True)
    rejection_reason = models.TextField(blank=True, null=True)
    
    # Tracking
    created_by = models.ForeignKey(
        'core.User', on_delete=models.SET_NULL, null=True, related_name='expenses_created'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'expenses'
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.expense_number} - {self.title}"
    
    def save(self, *args, **kwargs):
        if not self.expense_number:
            self.expense_number = self.generate_expense_number()
        super().save(*args, **kwargs)
    
    def generate_expense_number(self):
        """Generate unique expense number."""
        prefix = 'TBA-EXP'
        last_expense = Expense.objects.filter(
            expense_number__startswith=prefix
        ).order_by('-expense_number').first()
        
        if last_expense:
            try:
                last_num = int(last_expense.expense_number.split('-')[2])
                return f"{prefix}-{last_num + 1:06d}"
            except:
                pass
        return f"{prefix}-000001"
    
    def approve(self, user):
        """Approve expense."""
        self.status = 'approved'
        self.approved_by = user
        self.approved_at = timezone.now()
        self.save()
    
    def reject(self, user, reason=''):
        """Reject expense."""
        self.status = 'rejected'
        self.approved_by = user
        self.approved_at = timezone.now()
        self.rejection_reason = reason
        self.save()
    
    def mark_as_paid(self):
        """Mark expense as paid."""
        self.status = 'paid'
        self.save()


class RecurringExpense(models.Model):
    """Recurring expense model."""
    
    FREQUENCY_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.ForeignKey(
        ExpenseCategory, on_delete=models.SET_NULL, null=True
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    next_due_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_by = models.ForeignKey(
        'core.User', on_delete=models.SET_NULL, null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'recurring_expenses'
        ordering = ['next_due_date']
    
    def __str__(self):
        return f"{self.title} - {self.frequency}"
    
    def generate_next_expense(self):
        """Generate next expense instance."""
        from datetime import timedelta
        from dateutil.relativedelta import relativedelta
        
        if self.status != 'active':
            return None
        
        if self.end_date and self.next_due_date > self.end_date:
            return None
        
        # Create expense
        expense = Expense.objects.create(
            category=self.category,
            title=self.title,
            description=self.description,
            amount=self.amount,
            date=self.next_due_date,
            status='pending',
            created_by=self.created_by
        )
        
        # Update next due date
        if self.frequency == 'daily':
            self.next_due_date += timedelta(days=1)
        elif self.frequency == 'weekly':
            self.next_due_date += timedelta(weeks=1)
        elif self.frequency == 'monthly':
            self.next_due_date += relativedelta(months=1)
        elif self.frequency == 'quarterly':
            self.next_due_date += relativedelta(months=3)
        elif self.frequency == 'yearly':
            self.next_due_date += relativedelta(years=1)
        
        self.save()
        return expense


class Budget(models.Model):
    """Budget model for expense tracking."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.ForeignKey(
        ExpenseCategory, on_delete=models.CASCADE, related_name='budgets'
    )
    title = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField()
    alert_threshold = models.PositiveIntegerField(default=80, help_text='Alert when spending reaches this percentage')
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        'core.User', on_delete=models.SET_NULL, null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'budgets'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - ₦{self.amount}"
    
    @property
    def spent(self):
        """Calculate total spent in this budget period."""
        return Expense.objects.filter(
            category=self.category,
            date__gte=self.start_date,
            date__lte=self.end_date,
            status='paid'
        ).aggregate(total=models.Sum('amount'))['total'] or 0
    
    @property
    def remaining(self):
        """Calculate remaining budget."""
        return self.amount - self.spent
    
    @property
    def percentage_used(self):
        """Calculate percentage of budget used."""
        if self.amount > 0:
            return (self.spent / self.amount) * 100
        return 0
    
    @property
    def is_alert(self):
        """Check if budget alert should be triggered."""
        return self.percentage_used >= self.alert_threshold
