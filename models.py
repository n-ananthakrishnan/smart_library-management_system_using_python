from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, timedelta
import enum

db = SQLAlchemy()


class UserRole(enum.Enum):
    STUDENT = "student"
    LIBRARIAN = "librarian"
    ADMIN = "admin"


class BookStatus(enum.Enum):
    AVAILABLE = "available"
    BORROWED = "borrowed"
    RESERVED = "reserved"
    LOST = "lost"
    MAINTENANCE = "maintenance"


class User(UserMixin, db.Model):
    """User model for library members and staff"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    roll_number = db.Column(db.String(50))  # For students
    phone = db.Column(db.String(15))
    role = db.Column(db.Enum(UserRole), default=UserRole.STUDENT)
    profile_image = db.Column(db.String(200))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    borrowings = db.relationship('Borrowing', backref='user', lazy=True, cascade='all, delete-orphan')
    reservations = db.relationship('Reservation', backref='user', lazy=True, cascade='all, delete-orphan')
    reviews = db.relationship('Review', backref='user', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<User {self.username}>'

    def get_active_borrowings(self):
        return Borrowing.query.filter_by(user_id=self.id, returned_at=None).all()

    def get_total_borrowed(self):
        return len(self.get_active_borrowings())

    def has_overdue_books(self):
        active = self.get_active_borrowings()
        return any(b.is_overdue() for b in active)


class Book(db.Model):
    """Enhanced Book model"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False, index=True)
    author = db.Column(db.String(200), nullable=False)
    isbn = db.Column(db.String(20), unique=True, nullable=False)
    barcode = db.Column(db.String(100), unique=True, nullable=False, index=True)
    genre = db.Column(db.String(50), nullable=False, index=True)
    category = db.Column(db.String(100))
    rack_no = db.Column(db.String(20), nullable=False)
    shelf_no = db.Column(db.String(20))
    edition = db.Column(db.String(50))
    publication_year = db.Column(db.Integer)
    publisher = db.Column(db.String(200))
    pages = db.Column(db.Integer)
    description = db.Column(db.Text)
    
    # Book cover
    cover_image = db.Column(db.String(200))
    
    # Status tracking
    status = db.Column(db.Enum(BookStatus), default=BookStatus.AVAILABLE)
    total_copies = db.Column(db.Integer, default=1)
    available_copies = db.Column(db.Integer, default=1)
    
    # Ratings and reviews
    average_rating = db.Column(db.Float, default=0.0)
    
    # Metadata
    added_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_location_verified = db.Column(db.DateTime)

    # Relationships
    borrowings = db.relationship('Borrowing', backref='book', lazy=True, cascade='all, delete-orphan')
    reservations = db.relationship('Reservation', backref='book', lazy=True, cascade='all, delete-orphan')
    reviews = db.relationship('Review', backref='book', lazy=True, cascade='all, delete-orphan')
    activity_logs = db.relationship('ActivityLog', backref='book', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Book {self.title}>'

    def is_available(self):
        return self.available_copies > 0

    def get_current_borrower(self):
        borrowing = Borrowing.query.filter_by(book_id=self.id, returned_at=None).first()
        return borrowing.user if borrowing else None

    def get_borrowing_history(self, limit=5):
        return Borrowing.query.filter_by(book_id=self.id).order_by(
            Borrowing.borrowed_at.desc()
        ).limit(limit).all()


class Borrowing(db.Model):
    """Track book borrowing and returns"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False, index=True)
    borrowed_at = db.Column(db.DateTime, default=datetime.utcnow)
    due_date = db.Column(db.DateTime, nullable=False)
    returned_at = db.Column(db.DateTime)
    fine_paid = db.Column(db.Float, default=0.0)
    notes = db.Column(db.Text)

    def __repr__(self):
        return f'<Borrowing {self.user.username} - {self.book.title}>'

    def is_overdue(self):
        if self.returned_at:
            return False
        return datetime.utcnow() > self.due_date

    def get_days_overdue(self):
        if self.returned_at:
            return 0
        delta = datetime.utcnow() - self.due_date
        return max(0, delta.days)

    def calculate_fine(self, rate_per_day=10):
        """Calculate fine for overdue books (in rupees/currency)"""
        days_overdue = self.get_days_overdue()
        return days_overdue * rate_per_day


class Reservation(db.Model):
    """Track book reservations"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    reserved_at = db.Column(db.DateTime, default=datetime.utcnow)
    expected_return_date = db.Column(db.DateTime)
    is_fulfilled = db.Column(db.Boolean, default=False)
    fulfilled_at = db.Column(db.DateTime)
    canceled_at = db.Column(db.DateTime)

    def __repr__(self):
        return f'<Reservation {self.user.username} - {self.book.title}>'


class Review(db.Model):
    """Book reviews and ratings"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    review_text = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    helpful_count = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f'<Review {self.user.username} - {self.book.title}>'


class ActivityLog(db.Model):
    """Track all library activities for analytics"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'))
    action = db.Column(db.String(50), nullable=False)  # borrowed, returned, searched, etc.
    details = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    ip_address = db.Column(db.String(50))

    def __repr__(self):
        return f'<ActivityLog {self.action}>'


class Notification(db.Model):
    """Real-time notifications for users"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(50))  # overdue, available, reminder, etc.
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)

    def __repr__(self):
        return f'<Notification {self.title}>'
