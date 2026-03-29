"""
Utility functions for Tobaz Autos.
"""
import os
import uuid
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile


def log_activity(user, action, entity_type, entity_id='', description='', request=None):
    """Log user activity."""
    from .models import ActivityLog
    
    ip_address = None
    if request:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(',')[0]
        else:
            ip_address = request.META.get('REMOTE_ADDR')
    
    ActivityLog.objects.create(
        user=user,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        description=description,
        ip_address=ip_address
    )


def upload_to_backblaze(file, folder='uploads'):
    """Upload file to Backblaze B2."""
    if not settings.BACKBLAZE_B2_ENABLED:
        # Save locally if B2 is not enabled
        ext = file.name.split('.')[-1]
        filename = f"{folder}/{uuid.uuid4()}.{ext}"
        path = default_storage.save(filename, ContentFile(file.read()))
        return f"{settings.MEDIA_URL}{path}"
    
    try:
        from b2sdk.v2 import InMemoryAccountInfo, B2Api
        
        info = InMemoryAccountInfo()
        b2_api = B2Api(info)
        b2_api.authorize_account(
            "production",
            settings.BACKBLAZE_B2_KEY_ID,
            settings.BACKBLAZE_B2_APPLICATION_KEY
        )
        
        bucket = b2_api.get_bucket_by_name(settings.BACKBLAZE_B2_BUCKET_NAME)
        
        # Generate unique filename
        ext = file.name.split('.')[-1]
        filename = f"{folder}/{uuid.uuid4()}.{ext}"
        
        # Upload file
        file.seek(0)
        bucket.upload_bytes(
            data_bytes=file.read(),
            file_name=filename,
            content_type=file.content_type
        )
        
        # Return public URL
        return f"{settings.BACKBLAZE_B2_BUCKET_ENDPOINT}/{filename}"
    
    except Exception as e:
        print(f"Backblaze upload error: {e}")
        return None


def delete_from_backblaze(file_url):
    """Delete file from Backblaze B2."""
    if not settings.BACKBLAZE_B2_ENABLED:
        return True
    
    try:
        from b2sdk.v2 import InMemoryAccountInfo, B2Api
        
        info = InMemoryAccountInfo()
        b2_api = B2Api(info)
        b2_api.authorize_account(
            "production",
            settings.BACKBLAZE_B2_KEY_ID,
            settings.BACKBLAZE_B2_APPLICATION_KEY
        )
        
        bucket = b2_api.get_bucket_by_name(settings.BACKBLAZE_B2_BUCKET_NAME)
        
        # Extract filename from URL
        filename = file_url.split('/')[-1]
        
        # Delete file
        file_version = bucket.get_file_info_by_name(filename)
        b2_api.delete_file_version(
            file_version.id_,
            filename
        )
        
        return True
    
    except Exception as e:
        print(f"Backblaze delete error: {e}")
        return False


def format_currency(amount, currency='₦'):
    """Format amount as currency."""
    return f"{currency}{amount:,.2f}"


def generate_sku(category_code, product_id):
    """Generate SKU for product."""
    return f"{category_code}-{product_id:06d}"
