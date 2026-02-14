"""Management command to initialize the database with sample data."""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from library.models import Book, UserRole

User = get_user_model()


class Command(BaseCommand):
    help = 'Initialize the database with sample data'

    def handle(self, *args, **options):
        """Create sample data."""
        self.stdout.write(self.style.SUCCESS('Starting database initialization...'))

        # Create admin user
        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_superuser(
                username='admin',
                email='admin@library.com',
                password='admin123',
                first_name='Admin',
                last_name='User',
                role=UserRole.ADMIN
            )
            self.stdout.write(self.style.SUCCESS(f'Created admin user: {admin.username}'))
        else:
            self.stdout.write(self.style.WARNING('Admin user already exists'))

        # Create librarian user
        if not User.objects.filter(username='librarian').exists():
            librarian = User.objects.create_user(
                username='librarian',
                email='librarian@library.com',
                password='librarian123',
                first_name='John',
                last_name='Librarian',
                role=UserRole.LIBRARIAN
            )
            self.stdout.write(self.style.SUCCESS(f'Created librarian user: {librarian.username}'))
        else:
            self.stdout.write(self.style.WARNING('Librarian user already exists'))

        # Create sample student users
        for i in range(3):
            username = f'student{i+1}'
            if not User.objects.filter(username=username).exists():
                student = User.objects.create_user(
                    username=username,
                    email=f'student{i+1}@library.com',
                    password='student123',
                    first_name=f'Student',
                    last_name=f'User {i+1}',
                    roll_number=f'2024{i+1:03d}',
                    role=UserRole.STUDENT
                )
                self.stdout.write(self.style.SUCCESS(f'Created student user: {student.username}'))

        # Create sample books
        sample_books = [
            {
                'title': 'The Great Gatsby',
                'author': 'F. Scott Fitzgerald',
                'isbn': '9780743273565',
                'barcode': 'BAR001',
                'genre': 'Fiction',
                'rack_no': 'A1',
                'total_copies': 3,
            },
            {
                'title': 'To Kill a Mockingbird',
                'author': 'Harper Lee',
                'isbn': '9780061120084',
                'barcode': 'BAR002',
                'genre': 'Fiction',
                'rack_no': 'A2',
                'total_copies': 2,
            },
            {
                'title': 'Python Programming',
                'author': 'Guido van Rossum',
                'isbn': '9780135679913',
                'barcode': 'BAR003',
                'genre': 'Technology',
                'rack_no': 'B1',
                'total_copies': 4,
            },
            {
                'title': 'Django for Beginners',
                'author': 'William Vincent',
                'isbn': '9780999402701',
                'barcode': 'BAR004',
                'genre': 'Technology',
                'rack_no': 'B2',
                'total_copies': 2,
            },
        ]

        for book_data in sample_books:
            if not Book.objects.filter(isbn=book_data['isbn']).exists():
                book_data['available_copies'] = book_data['total_copies']
                book = Book.objects.create(**book_data)
                self.stdout.write(self.style.SUCCESS(f'Created book: {book.title}'))
            else:
                self.stdout.write(self.style.WARNING(f'Book already exists: {book_data["title"]}'))

        self.stdout.write(self.style.SUCCESS('Database initialization completed!'))
