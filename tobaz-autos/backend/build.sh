#!/usr/bin/env bash
# Build script for Render deployment

set -o errexit

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Collecting static files..."
python manage.py collectstatic --no-input

echo "Running migrations..."
python manage.py migrate

echo "Creating default admin user..."
python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@tobazautos.com', 'admin123')
    print('Default admin user created: admin / admin123')
EOF

echo "Build completed!"
