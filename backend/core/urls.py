"""
URL configuration for Core app.
"""
from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('login/', views.LoginView.as_view(), name='login'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/change-password/', views.ChangePasswordView.as_view(), name='change-password'),
    path('profile/upload-image/', views.ProfileImageUploadView.as_view(), name='upload-profile-image'),
    
    # Users
    path('users/', views.UserListView.as_view(), name='user-list'),
    path('users/<uuid:id>/', views.UserDetailView.as_view(), name='user-detail'),
    
    # Activity Logs
    path('activity-logs/', views.ActivityLogListView.as_view(), name='activity-logs'),
    
    # Notifications
    path('notifications/', views.NotificationListView.as_view(), name='notifications'),
    path('notifications/<uuid:pk>/read/', views.NotificationMarkReadView.as_view(), name='notification-read'),
    
    # Settings
    path('settings/', views.SettingListView.as_view(), name='settings'),
    path('settings/<str:key>/', views.SettingUpdateView.as_view(), name='setting-update'),
]
