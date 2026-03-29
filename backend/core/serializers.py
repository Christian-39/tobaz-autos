"""
Serializers for Core app.
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import ActivityLog, Notification, Setting

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """User serializer."""
    
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'full_name',
            'role', 'phone', 'profile_image', 'address', 'is_active',
            'date_joined', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'date_joined', 'created_at', 'updated_at']


class UserCreateSerializer(serializers.ModelSerializer):
    """User creation serializer."""
    
    password = serializers.CharField(write_only=True, min_length=6)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'password', 'first_name', 'last_name',
            'role', 'phone', 'address'
        ]
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """User update serializer."""
    
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'email', 'role', 'phone', 
            'profile_image', 'address', 'is_active'
        ]


class ChangePasswordSerializer(serializers.Serializer):
    """Password change serializer."""
    
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=6)


class LoginSerializer(serializers.Serializer):
    """Login serializer."""
    
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)


class LoginResponseSerializer(serializers.Serializer):
    """Login response serializer."""
    
    token = serializers.CharField()
    user = UserSerializer()


class ActivityLogSerializer(serializers.ModelSerializer):
    """Activity log serializer."""
    
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = ActivityLog
        fields = [
            'id', 'user', 'user_name', 'action', 'entity_type', 
            'entity_id', 'description', 'ip_address', 'created_at'
        ]


class NotificationSerializer(serializers.ModelSerializer):
    """Notification serializer."""
    
    class Meta:
        model = Notification
        fields = [
            'id', 'title', 'message', 'notification_type', 
            'is_read', 'link', 'created_at'
        ]


class SettingSerializer(serializers.ModelSerializer):
    """Setting serializer."""
    
    class Meta:
        model = Setting
        fields = ['id', 'key', 'value', 'description', 'updated_at']
