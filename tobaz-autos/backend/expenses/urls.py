"""
URL configuration for Expenses app.
"""
from django.urls import path
from . import views

urlpatterns = [
    # Categories
    path('categories/', views.ExpenseCategoryListView.as_view(), name='expense-category-list'),
    path('categories/<uuid:id>/', views.ExpenseCategoryDetailView.as_view(), name='expense-category-detail'),
    
    # Expenses
    path('', views.ExpenseListView.as_view(), name='expense-list'),
    path('<uuid:id>/', views.ExpenseDetailView.as_view(), name='expense-detail'),
    path('<uuid:id>/approval/', views.ExpenseApprovalView.as_view(), name='expense-approval'),
    path('<uuid:id>/receipt/', views.ExpenseReceiptUploadView.as_view(), name='expense-receipt'),
    
    # Recurring Expenses
    path('recurring/', views.RecurringExpenseListView.as_view(), name='recurring-expense-list'),
    path('recurring/<uuid:id>/', views.RecurringExpenseDetailView.as_view(), name='recurring-expense-detail'),
    path('recurring/<uuid:id>/generate/', views.GenerateRecurringExpenseView.as_view(), name='recurring-expense-generate'),
    
    # Budgets
    path('budgets/', views.BudgetListView.as_view(), name='budget-list'),
    path('budgets/<uuid:id>/', views.BudgetDetailView.as_view(), name='budget-detail'),
    
    # Stats
    path('stats/overview/', views.ExpenseStatsView.as_view(), name='expense-stats'),
    path('stats/chart/', views.ExpenseChartView.as_view(), name='expense-chart'),
]
