"""Context processors for library app."""
from .models import Notification, UserRole


def library_context(request):
    """Add library-specific context to all templates."""
    context = {
        'site_name': 'Smart Library Management',
        'UserRole': UserRole,
    }

    if request.user.is_authenticated:
        # Add unread notifications count
        unread_count = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).count()
        context['unread_notifications_count'] = unread_count

        # Add user role
        context['user_role'] = request.user.role

    return context
