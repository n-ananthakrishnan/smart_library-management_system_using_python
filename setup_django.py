#!/usr/bin/env python
"""Setup script for Django."""
import os
import django
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_library.settings')
django.setup()

from django.core.management import call_command
from django.contrib.auth import get_user_model

User = get_user_model()

print("=" * 60)
print("Smart Library Management System - Django Setup")
print("=" * 60)

# Run migrations
print("\n1. Running migrations...")
call_command('migrate', verbosity=1)

# Create sample data
print("\n2. Creating sample data...")
call_command('init_db', verbosity=1)

# Create superuser if needed
print("\n3. Checking superuser...")
if not User.objects.filter(username='admin').exists():
    print("No admin user found. Creating one...")
    User.objects.create_superuser(
        username='admin',
        email='admin@library.com',
        password='admin123'
    )
    print("Admin user created: username=admin, password=admin123")
else:
    print("Admin user already exists")

print("\n" + "=" * 60)
print("Setup complete!")
print("=" * 60)
print("\nTo start the development server:")
print("  python manage.py runserver")
print("\nTo start with WebSocket support (Channels):")
print("  daphne -b 0.0.0.0 -p 8000 smart_library.asgi:application")
print("\nAdmin interface:")
print("  http://localhost:8000/admin/")
