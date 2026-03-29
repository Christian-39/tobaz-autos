"""
Admin configuration for Core app.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, ActivityLog, Notification, Setting


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """User admin configuration."""
    
    list_display = [
        'username', 'email', 'first_name', 'last_name', 'role',
        'is_active', 'date_joined'
    ]
    list_filter = ['role', 'is_active', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('role', 'phone', 'profile_image', 'address')
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Additional Info', {
            'fields': ('role', 'phone')
        }),
    )


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    """Activity log admin configuration."""
    
    list_display = ['user', 'action', 'entity_type', 'description', 'created_at']
    list_filter = ['action', 'entity_type', 'created_at']
    search_fields = ['user__username', 'description']
    readonly_fields = ['user', 'action', 'entity_type', 'entity_id', 'description', 'ip_address', 'created_at']
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Notification admin configuration."""
    
    list_display = ['title', 'user', 'notification_type', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['title', 'message', 'user__username']


@admin.register(Setting)
class SettingAdmin(admin.ModelAdmin):
    """Setting admin configuration."""
    
    list_display = ['key', 'value', 'description', 'updated_at']
    search_fields = ['key', 'description']
