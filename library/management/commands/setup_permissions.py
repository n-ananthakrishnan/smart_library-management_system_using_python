"""Django Management Commands and Admin Interface Setup"""
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from library.models import Book

User = get_user_model()


def setup_permissions():
    """Setup custom permissions."""
    content_type = ContentType.objects.get_for_model(Book)
    
    # Create custom permissions
    permission, created = Permission.objects.get_or_create(
        codename='can_manage_books',
        name='Can manage books',
        content_type=content_type,
    )
    
    if created:
        print('Permission "can_manage_books" created')
    else:
        print('Permission "can_manage_books" already exists')
