"""
URL configuration for Tobaz Autos.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('core.urls')),
    path('api/inventory/', include('inventory.urls')),
    path('api/shipments/', include('shipments.urls')),
    path('api/sales/', include('sales.urls')),
    path('api/expenses/', include('expenses.urls')),
    path('api/dashboard/', include('core.dashboard_urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Serve React frontend for all other routes
urlpatterns += [
    path('', TemplateView.as_view(template_name='index.html')),
    path('<path:path>', TemplateView.as_view(template_name='index.html')),
]
