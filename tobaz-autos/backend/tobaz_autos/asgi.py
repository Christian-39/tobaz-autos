"""
ASGI config for Tobaz Autos.
"""
import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tobaz_autos.settings')

application = get_asgi_application()
