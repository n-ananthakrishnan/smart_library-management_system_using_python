"""
Models for the smart library management system.
"""

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import datetime, timedelta
from django.utils import timezone
import enum


class UserRole(models.TextChoices):
    STUDENT = 'student', 'Student'
    LIBRARIAN = 'librarian', 'Librarian'
    ADMIN = 'admin', 'Admin'


class BookStatus(models.TextChoices):
    AVAILABLE = 'available', 'Available'
    BORROWED = 'borrowed', 'Borrowed'
    RESERVED = 'reserved', 'Reserved'
    LOST = 'lost', 'Lost'
    MAINTENANCE = 'maintenance', 'Maintenance'


class User(AbstractUser):
    """Extended User model for library members and staff"""
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.STUDENT
    )
    roll_number = models.CharField(max_length=50, blank=True, null=True)  # For students
    phone = models.CharField(max_length=15, blank=True, null=True)
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['username']),
            models.Index(fields=['email']),
            models.Index(fields=['role']),
        ]

    def __str__(self):
        return self.username

    def get_active_borrowings(self):
        """Get all active (not returned) borrowings"""
        return self.borrowings.filter(returned_at__isnull=True)

    def get_total_borrowed(self):
        """Get count of active borrowings"""
        return self.get_active_borrowings().count()

    def has_overdue_books(self):
        """Check if user has any overdue books"""
        active = self.get_active_borrowings()
        return any(b.is_overdue() for b in active)


class Book(models.Model):
    """Enhanced Book model"""
    title = models.CharField(max_length=200, db_index=True)
    author = models.CharField(max_length=200)
    isbn = models.CharField(max_length=20, unique=True)
    barcode = models.CharField(max_length=100, unique=True, db_index=True)
    genre = models.CharField(max_length=50, db_index=True)
    category = models.CharField(max_length=100, blank=True)
    rack_no = models.CharField(max_length=20)
    shelf_no = models.CharField(max_length=20, blank=True)
    edition = models.CharField(max_length=50, blank=True)
    publication_year = models.IntegerField(blank=True, null=True)
    publisher = models.CharField(max_length=200, blank=True)
    pages = models.IntegerField(blank=True, null=True)
    description = models.TextField(blank=True)

    # Book cover
    cover_image = models.ImageField(upload_to='book_covers/', blank=True, null=True)

    # Status tracking
    status = models.CharField(
        max_length=20,
        choices=BookStatus.choices,
        default=BookStatus.AVAILABLE
    )
    total_copies = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    available_copies = models.IntegerField(default=1, validators=[MinValueValidator(0)])

    # Ratings and reviews
    average_rating = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)]
    )

    # Metadata
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_location_verified = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-added_at']
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['isbn']),
            models.Index(fields=['barcode']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return self.title

    def is_available(self):
        """Check if book has available copies"""
        return self.available_copies > 0

    def get_current_borrower(self):
        """Get the current borrower of this book"""
        borrowing = self.borrowings.filter(returned_at__isnull=True).first()
        return borrowing.user if borrowing else None

    def get_borrowing_history(self, limit=5):
        """Get borrowing history"""
        return self.borrowings.order_by('-borrowed_at')[:limit]


class Borrowing(models.Model):
    """Track book borrowing and returns"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='borrowings')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='borrowings')
    borrowed_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField()
    returned_at = models.DateTimeField(blank=True, null=True)
    fine_paid = models.FloatField(default=0.0)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-borrowed_at']
        indexes = [
            models.Index(fields=['user', 'returned_at']),
            models.Index(fields=['book', 'returned_at']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.book.title}"

    def is_overdue(self):
        """Check if book is overdue"""
        if self.returned_at:
            return False
        return timezone.now() > self.due_date

    def get_days_overdue(self):
        """Get number of days overdue"""
        if self.returned_at:
            return 0
        delta = timezone.now() - self.due_date
        return max(0, delta.days)

    def calculate_fine(self, rate_per_day=10):
        """Calculate fine for overdue books"""
        days_overdue = self.get_days_overdue()
        return days_overdue * rate_per_day


class Reservation(models.Model):
    """Track book reservations"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reservations')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reservations')
    reserved_at = models.DateTimeField(auto_now_add=True)
    expected_return_date = models.DateTimeField(blank=True, null=True)
    is_fulfilled = models.BooleanField(default=False)
    fulfilled_at = models.DateTimeField(blank=True, null=True)
    canceled_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-reserved_at']
        indexes = [
            models.Index(fields=['user', 'is_fulfilled']),
            models.Index(fields=['book', 'is_fulfilled']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.book.title}"


class Review(models.Model):
    """Book reviews and ratings"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    review_text = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    helpful_count = models.IntegerField(default=0)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('user', 'book')
        indexes = [
            models.Index(fields=['book']),
            models.Index(fields=['user']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.book.title} ({self.rating}⭐)"


class ActivityLog(models.Model):
    """Track all library activities for analytics"""
    ACTION_CHOICES = [
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('search', 'Search'),
        ('view_book', 'View Book'),
        ('borrow', 'Borrow'),
        ('return', 'Return'),
        ('reserve', 'Reserve'),
        ('add_book', 'Add Book'),
        ('edit_book', 'Edit Book'),
        ('delete_book', 'Delete Book'),
        ('scan_success', 'Scan Success'),
        ('scan_misplaced', 'Scan Misplaced'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name='activity_logs')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, blank=True, null=True, related_name='activity_logs')
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    details = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    ip_address = models.CharField(max_length=50, blank=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['action', 'timestamp']),
        ]

    def __str__(self):
        return f"{self.action} - {self.timestamp}"


class Notification(models.Model):
    """Real-time notifications for users"""
    TYPE_CHOICES = [
        ('overdue', 'Overdue'),
        ('available', 'Available'),
        ('reminder', 'Reminder'),
        ('borrow', 'Borrow'),
        ('reservation', 'Reservation'),
        ('info', 'Info'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    type = models.CharField(max_length=50, choices=TYPE_CHOICES, default='info')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['expires_at']),
        ]

    def __str__(self):
        return self.title
