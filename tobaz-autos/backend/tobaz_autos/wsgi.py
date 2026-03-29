"""
WSGI config for Tobaz Autos.
"""
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tobaz_autos.settings')

application = get_wsgi_application()
