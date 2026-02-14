"""Tests for the library app."""
from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Book, BookStatus, UserRole, Borrowing, Review
from datetime import timedelta
from django.utils import timezone

User = get_user_model()


class UserModelTests(TestCase):
    """Tests for User model."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            role=UserRole.STUDENT
        )

    def test_user_creation(self):
        """Test user creation."""
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.role, UserRole.STUDENT)

    def test_get_active_borrowings(self):
        """Test getting active borrowings."""
        book = Book.objects.create(
            title='Test Book',
            author='Test Author',
            isbn='123456',
            barcode='BAR123',
            genre='Fiction',
            rack_no='A1'
        )
        borrowing = Borrowing.objects.create(
            user=self.user,
            book=book,
            due_date=timezone.now() + timedelta(days=14)
        )
        active = self.user.get_active_borrowings()
        self.assertEqual(active.count(), 1)
        self.assertEqual(active[0], borrowing)


class BookModelTests(TestCase):
    """Tests for Book model."""

    def setUp(self):
        self.book = Book.objects.create(
            title='Test Book',
            author='Test Author',
            isbn='123456',
            barcode='BAR123',
            genre='Fiction',
            rack_no='A1',
            total_copies=3,
            available_copies=3
        )

    def test_book_is_available(self):
        """Test book availability."""
        self.assertTrue(self.book.is_available())
        self.book.available_copies = 0
        self.assertFalse(self.book.is_available())

    def test_get_current_borrower(self):
        """Test getting current borrower."""
        user = User.objects.create_user('testuser', 'test@example.com', 'pass123')
        borrowing = Borrowing.objects.create(
            user=user,
            book=self.book,
            due_date=timezone.now() + timedelta(days=14)
        )
        self.assertEqual(self.book.get_current_borrower(), user)


class BorrowingModelTests(TestCase):
    """Tests for Borrowing model."""

    def setUp(self):
        self.user = User.objects.create_user('testuser', 'test@example.com', 'pass123')
        self.book = Book.objects.create(
            title='Test Book',
            author='Test Author',
            isbn='123456',
            barcode='BAR123',
            genre='Fiction',
            rack_no='A1'
        )
        self.borrowing = Borrowing.objects.create(
            user=self.user,
            book=self.book,
            due_date=timezone.now() + timedelta(days=14)
        )

    def test_borrowing_is_not_overdue(self):
        """Test non-overdue borrowing."""
        self.assertFalse(self.borrowing.is_overdue())

    def test_borrowing_is_overdue(self):
        """Test overdue borrowing."""
        self.borrowing.due_date = timezone.now() - timedelta(days=1)
        self.borrowing.save()
        self.assertTrue(self.borrowing.is_overdue())

    def test_calculate_fine(self):
        """Test fine calculation."""
        self.borrowing.due_date = timezone.now() - timedelta(days=3)
        self.borrowing.save()
        fine = self.borrowing.calculate_fine(rate_per_day=10)
        self.assertEqual(fine, 30)
