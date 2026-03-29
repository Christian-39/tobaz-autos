"""
Views for Core app.
"""
from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from django.db.models import Q
from .models import ActivityLog, Notification, Setting
from .serializers import (
    UserSerializer, UserCreateSerializer, UserUpdateSerializer,
    ChangePasswordSerializer, LoginSerializer, ActivityLogSerializer,
    NotificationSerializer, SettingSerializer
)
from .authentication import generate_jwt_token
from .utils import log_activity, upload_to_backblaze

User = get_user_model()


class LoginView(APIView):
    """User login view."""
    
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        
        user = authenticate(username=username, password=password)
        
        if not user:
            return Response(
                {'error': 'Invalid credentials'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        if not user.is_active:
            return Response(
                {'error': 'Account is disabled'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        token = generate_jwt_token(user)
        log_activity(user, 'login', 'User', str(user.id), 'User logged in', request)
        
        return Response({
            'token': token,
            'user': UserSerializer(user).data
        })


class RegisterView(APIView):
    """User registration view."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        # Only admins can create new users
        if not request.user.is_admin:
            return Response(
                {'error': 'Only admins can create users'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = UserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        log_activity(
            request.user, 'create', 'User', str(user.id),
            f'Created user {user.username}', request
        )
        
        return Response(
            UserSerializer(user).data,
            status=status.HTTP_201_CREATED
        )


class UserListView(generics.ListAPIView):
    """List all users."""
    
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = User.objects.all()
        search = self.request.query_params.get('search', '')
        role = self.request.query_params.get('role', '')
        
        if search:
            queryset = queryset.filter(
                Q(username__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(email__icontains=search)
            )
        
        if role:
            queryset = queryset.filter(role=role)
        
        return queryset


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a user."""
    
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return UserUpdateSerializer
        return UserSerializer
    
    def update(self, request, *args, **kwargs):
        # Only admins can update other users
        user = self.get_object()
        if not request.user.is_admin and request.user.id != user.id:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        response = super().update(request, *args, **kwargs)
        log_activity(
            request.user, 'update', 'User', str(user.id),
            f'Updated user {user.username}', request
        )
        return response
    
    def destroy(self, request, *args, **kwargs):
        if not request.user.is_admin:
            return Response(
                {'error': 'Only admins can delete users'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        user = self.get_object()
        log_activity(
            request.user, 'delete', 'User', str(user.id),
            f'Deleted user {user.username}', request
        )
        return super().destroy(request, *args, **kwargs)


class ChangePasswordView(APIView):
    """Change password view."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        old_password = serializer.validated_data['old_password']
        new_password = serializer.validated_data['new_password']
        
        if not user.check_password(old_password):
            return Response(
                {'error': 'Current password is incorrect'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.set_password(new_password)
        user.save()
        
        log_activity(
            user, 'update', 'User', str(user.id),
            'Password changed', request
        )
        
        return Response({'message': 'Password changed successfully'})


class ProfileView(APIView):
    """Get and update current user profile."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        return Response(UserSerializer(request.user).data)
    
    def put(self, request):
        serializer = UserUpdateSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        log_activity(
            request.user, 'update', 'User', str(request.user.id),
            'Updated profile', request
        )
        
        return Response(UserSerializer(request.user).data)


class ProfileImageUploadView(APIView):
    """Upload profile image."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        if 'image' not in request.FILES:
            return Response(
                {'error': 'No image provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        image = request.FILES['image']
        user = request.user
        
        # Upload to Backblaze B2
        image_url = upload_to_backblaze(image, f'profiles/{user.id}')
        
        if not image_url:
            return Response(
                {'error': 'Failed to upload image'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        user.profile_image = image_url
        user.save()
        
        log_activity(
            user, 'update', 'User', str(user.id),
            'Profile image updated', request
        )
        
        return Response({'profile_image': image_url})


class ActivityLogListView(generics.ListAPIView):
    """List activity logs."""
    
    serializer_class = ActivityLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Only admins and managers can view all logs
        if not self.request.user.is_manager:
            return ActivityLog.objects.filter(user=self.request.user)
        
        queryset = ActivityLog.objects.all()
        user_id = self.request.query_params.get('user', '')
        action = self.request.query_params.get('action', '')
        
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        if action:
            queryset = queryset.filter(action=action)
        
        return queryset[:100]  # Limit to last 100 logs


class NotificationListView(generics.ListAPIView):
    """List user notifications."""
    
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)


class NotificationMarkReadView(APIView):
    """Mark notification as read."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        try:
            notification = Notification.objects.get(id=pk, user=request.user)
            notification.is_read = True
            notification.save()
            return Response({'message': 'Notification marked as read'})
        except Notification.DoesNotExist:
            return Response(
                {'error': 'Notification not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class SettingListView(generics.ListAPIView):
    """List all settings."""
    
    queryset = Setting.objects.all()
    serializer_class = SettingSerializer
    permission_classes = [permissions.IsAuthenticated]


class SettingUpdateView(APIView):
    """Update a setting."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def put(self, request, key):
        if not request.user.is_admin:
            return Response(
                {'error': 'Only admins can update settings'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            setting = Setting.objects.get(key=key)
            setting.value = request.data.get('value', setting.value)
            setting.save()
            return Response(SettingSerializer(setting).data)
        except Setting.DoesNotExist:
            return Response(
                {'error': 'Setting not found'},
                status=status.HTTP_404_NOT_FOUND
            )
