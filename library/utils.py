"""Utility functions for the library app."""
from .models import ActivityLog, Notification
from django.utils import timezone
from datetime import timedelta


def log_activity(request, action, book=None, user=None, details=None):
    """Log user activities."""
    activity = ActivityLog.objects.create(
        user=user or (request.user if request.user.is_authenticated else None),
        book=book,
        action=action,
        details=details,
        ip_address=get_client_ip(request)
    )
    return activity


def create_notification(user, title, message, notification_type):
    """Create a notification for a user."""
    notification = Notification.objects.create(
        user=user,
        title=title,
        message=message,
        type=notification_type,
        expires_at=timezone.now() + timedelta(days=30)
    )
    return notification


def get_client_ip(request):
    """Get client IP address from request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
