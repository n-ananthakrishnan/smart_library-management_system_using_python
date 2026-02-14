"""Signal handlers for the library app."""
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta

from library.models import Borrowing, Book, Reservation


@receiver(post_save, sender=Borrowing)
def handle_borrowing_created(sender, instance, created, **kwargs):
    """Handle when a book is borrowed."""
    if created:
        # Update book status
        if instance.book.available_copies == 0:
            instance.book.status = 'borrowed'
            instance.book.save()


@receiver(post_save, sender=Borrowing)
def handle_borrowing_returned(sender, instance, **kwargs):
    """Handle when a book is returned."""
    if instance.returned_at and not kwargs.get('created'):
        # Check if any reservations are waiting
        reservation = Reservation.objects.filter(
            book=instance.book,
            is_fulfilled=False,
            canceled_at__isnull=True
        ).first()

        if reservation:
            # Notify the user who reserved it
            from library.models import Notification
            Notification.objects.create(
                user=reservation.user,
                title='Reserved Book Available',
                message=f'The book "{instance.book.title}" you reserved is now available!',
                type='available',
                expires_at=timezone.now() + timedelta(days=7)
            )
            reservation.is_fulfilled = True
            reservation.fulfilled_at = timezone.now()
            reservation.save()
