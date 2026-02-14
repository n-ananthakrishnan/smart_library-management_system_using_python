from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_socketio import SocketIO, emit, join_room, leave_room
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import cv2
from pyzbar.pyzbar import decode
import qrcode
from io import BytesIO
import base64
import os
from functools import wraps
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from models import (
    db, User, Book, Borrowing, Reservation, Review, ActivityLog, Notification,
    UserRole, BookStatus
)

# Flask app configuration
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-key-change-in-production-12345678')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///smart_library.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = int(os.environ.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize extensions
db.init_app(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Load user for login manager
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def librarian_required(f):
    """Decorator for librarian-only routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role == UserRole.STUDENT:
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function


def log_activity(action, book_id=None, user_id=None, details=None):
    """Log user activities"""
    activity = ActivityLog(
        user_id=user_id or (current_user.id if current_user.is_authenticated else None),
        book_id=book_id,
        action=action,
        details=details,
        ip_address=request.remote_addr
    )
    db.session.add(activity)
    db.session.commit()


def create_notification(user_id, title, message, notification_type):
    """Create a notification for a user"""
    notification = Notification(
        user_id=user_id,
        title=title,
        message=message,
        type=notification_type,
        expires_at=datetime.utcnow() + timedelta(days=30)
    )
    db.session.add(notification)
    db.session.commit()
    
    # Emit real-time notification via WebSocket
    socketio.emit('notification', {
        'title': title,
        'message': message,
        'type': notification_type
    }, room=f'user_{user_id}')


# ============== AUTHENTICATION ROUTES ==============

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        full_name = request.form.get('full_name')
        roll_number = request.form.get('roll_number')

        if not all([username, email, password, confirm_password, full_name]):
            flash('All fields are required!', 'danger')
            return redirect(url_for('register'))

        if password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return redirect(url_for('register'))

        if User.query.filter_by(username=username).first():
            flash('Username already exists!', 'danger')
            return redirect(url_for('register'))

        if User.query.filter_by(email=email).first():
            flash('Email already registered!', 'danger')
            return redirect(url_for('register'))

        # Create new user
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            full_name=full_name,
            roll_number=roll_number
        )
        db.session.add(user)
        db.session.commit()

        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password_hash, password):
            if not user.is_active:
                flash('Your account has been deactivated.', 'danger')
                return redirect(url_for('login'))

            login_user(user)
            log_activity('login')
            flash(f'Welcome back, {user.full_name}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password!', 'danger')

    return render_template('login.html')


@app.route('/logout', methods=['POST'])
@login_required
def logout():
    """User logout"""
    log_activity('logout')
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))


# ============== MAIN ROUTES ==============

@app.route('/')
def index():
    """Home/Landing page"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    book_count = Book.query.count()
    user_count = User.query.count()
    total_borrowed = Borrowing.query.filter_by(returned_at=None).count()

    return render_template(
        'index.html',
        book_count=book_count,
        user_count=user_count,
        total_borrowed=total_borrowed
    )


@app.route('/dashboard')
@login_required
def dashboard():
    """User dashboard with personalized data"""
    if current_user.role in [UserRole.LIBRARIAN, UserRole.ADMIN]:
        # Librarian dashboard
        total_books = Book.query.count()
        available_books = Book.query.filter_by(status=BookStatus.AVAILABLE).count()
        total_members = User.query.filter_by(role=UserRole.STUDENT).count()
        active_borrowings = Borrowing.query.filter_by(returned_at=None).count()
        overdue_count = sum(1 for b in Borrowing.query.filter_by(returned_at=None).all() if b.is_overdue())

        # Recent activities
        recent_activities = ActivityLog.query.order_by(ActivityLog.timestamp.desc()).limit(10).all()

        return render_template(
            'librarian_dashboard.html',
            total_books=total_books,
            available_books=available_books,
            total_members=total_members,
            active_borrowings=active_borrowings,
            overdue_count=overdue_count,
            recent_activities=recent_activities
        )
    else:
        # Student dashboard
        active_borrowings = current_user.get_active_borrowings()
        overdue_count = sum(1 for b in active_borrowings if b.is_overdue())
        total_fine = sum(b.calculate_fine() for b in active_borrowings if b.is_overdue())

        notifications = Notification.query.filter_by(
            user_id=current_user.id,
            is_read=False
        ).order_by(Notification.created_at.desc()).all()

        return render_template(
            'student_dashboard.html',
            active_borrowings=active_borrowings,
            overdue_count=overdue_count,
            total_fine=total_fine,
            notifications=notifications
        )


# ============== BOOK MANAGEMENT ROUTES ==============

@app.route('/books')
@login_required
def view_books():
    """View all books with search and filter"""
    page = request.args.get('page', 1, type=int)
    search_query = request.args.get('q', '')
    genre_filter = request.args.get('genre', '')
    status_filter = request.args.get('status', '')

    query = Book.query

    if search_query:
        query = query.filter(
            (Book.title.ilike(f'%{search_query}%')) |
            (Book.author.ilike(f'%{search_query}%')) |
            (Book.isbn.ilike(f'%{search_query}%'))
        )
        log_activity('search', details=f'Searched: {search_query}')

    if genre_filter:
        query = query.filter_by(genre=genre_filter)

    if status_filter and current_user.role in [UserRole.LIBRARIAN, UserRole.ADMIN]:
        query = query.filter_by(status=BookStatus[status_filter.upper()])

    books = query.paginate(page=page, per_page=12)
    genres = db.session.query(Book.genre).distinct().all()

    return render_template(
        'list_books.html',
        books=books,
        genres=[g[0] for g in genres],
        search_query=search_query,
        genre_filter=genre_filter
    )


@app.route('/book/<int:book_id>')
@login_required
def view_book_detail(book_id):
    """View book details and reviews"""
    book = Book.query.get_or_404(book_id)
    reviews = Review.query.filter_by(book_id=book_id).order_by(Review.created_at.desc()).all()
    user_review = None

    if current_user.is_authenticated:
        user_review = Review.query.filter_by(
            book_id=book_id,
            user_id=current_user.id
        ).first()

    log_activity('view_book', book_id=book_id)

    return render_template(
        'book_detail.html',
        book=book,
        reviews=reviews,
        user_review=user_review
    )


@app.route('/add_book', methods=['GET', 'POST'])
@login_required
@librarian_required
def add_book():
    """Add a new book (Librarian only)"""
    if request.method == 'POST':
        title = request.form.get('title')
        author = request.form.get('author')
        isbn = request.form.get('isbn')
        barcode = request.form.get('barcode')
        genre = request.form.get('genre')
        category = request.form.get('category')
        rack_no = request.form.get('rack_no')
        shelf_no = request.form.get('shelf_no')
        edition = request.form.get('edition')
        publication_year = request.form.get('publication_year')
        publisher = request.form.get('publisher')
        pages = request.form.get('pages')
        description = request.form.get('description')
        total_copies = request.form.get('total_copies', 1, type=int)

        if not all([title, author, isbn, barcode, genre, rack_no]):
            flash('Please fill all required fields!', 'danger')
            return redirect(url_for('add_book'))

        if Book.query.filter_by(isbn=isbn).first():
            flash('ISBN already exists!', 'danger')
            return redirect(url_for('add_book'))

        if Book.query.filter_by(barcode=barcode).first():
            flash('Barcode already exists!', 'danger')
            return redirect(url_for('add_book'))

        book = Book(
            title=title,
            author=author,
            isbn=isbn,
            barcode=barcode,
            genre=genre,
            category=category,
            rack_no=rack_no,
            shelf_no=shelf_no,
            edition=edition,
            publication_year=publication_year,
            publisher=publisher,
            pages=pages,
            description=description,
            total_copies=total_copies,
            available_copies=total_copies
        )
        db.session.add(book)
        db.session.commit()

        log_activity('add_book', book_id=book.id)
        flash(f'Book "{title}" added successfully!', 'success')
        return redirect(url_for('view_book_detail', book_id=book.id))

    return render_template('add_book.html')


@app.route('/edit/<int:book_id>', methods=['GET', 'POST'])
@login_required
@librarian_required
def edit_book(book_id):
    """Edit book details"""
    book = Book.query.get_or_404(book_id)

    if request.method == 'POST':
        book.title = request.form.get('title')
        book.author = request.form.get('author')
        book.isbn = request.form.get('isbn')
        book.barcode = request.form.get('barcode')
        book.genre = request.form.get('genre')
        book.category = request.form.get('category')
        book.rack_no = request.form.get('rack_no')
        book.shelf_no = request.form.get('shelf_no')
        book.edition = request.form.get('edition')
        book.publication_year = request.form.get('publication_year')
        book.publisher = request.form.get('publisher')
        book.pages = request.form.get('pages')
        book.description = request.form.get('description')
        book.updated_at = datetime.utcnow()

        db.session.commit()
        log_activity('edit_book', book_id=book_id)
        flash('Book updated successfully!', 'success')
        return redirect(url_for('view_book_detail', book_id=book_id))

    return render_template('edit_book.html', book=book)


@app.route('/delete/<int:book_id>', methods=['POST'])
@login_required
@librarian_required
def delete_book(book_id):
    """Delete a book"""
    book = Book.query.get_or_404(book_id)
    title = book.title
    db.session.delete(book)
    db.session.commit()

    log_activity('delete_book', book_id=book_id)
    flash(f'Book "{title}" deleted successfully!', 'success')
    return redirect(url_for('view_books'))


# ============== BARCODE & QR CODE ROUTES ==============

@app.route('/scan', methods=['GET', 'POST'])
@login_required
def scan_book():
    """Barcode scanning page"""
    if request.method == 'POST':
        rack_no = request.form.get('rack_no')
        if not rack_no:
            return render_template('scan.html', error="Please enter a rack number.")

        # Initialize camera
        cap = cv2.VideoCapture(0)
        scanned_data = None

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            barcodes = decode(frame)
            for barcode in barcodes:
                scanned_data = barcode.data.decode('utf-8')
                break

            if scanned_data:
                break

            cv2.imshow("Barcode Scanner", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

        if not scanned_data:
            return render_template('scan.html', error="No barcode detected. Try again.")

        book = Book.query.filter_by(barcode=scanned_data).first()
        if book:
            if book.rack_no == rack_no:
                recommendations = Book.query.filter(
                    Book.genre == book.genre,
                    Book.id != book.id,
                    Book.status == BookStatus.AVAILABLE
                ).limit(3).all()

                log_activity('scan_success', book_id=book.id)
                return render_template(
                    'scan_result.html',
                    success=True,
                    message=f"✓ '{book.title}' is in the correct rack!",
                    book=book,
                    recommendations=recommendations
                )
            else:
                log_activity('scan_misplaced', book_id=book.id)
                return render_template(
                    'scan_result.html',
                    success=False,
                    message=f"✗ '{book.title}' is in the wrong rack. Should be in rack {book.rack_no}",
                    book=book
                )
        else:
            return render_template(
                'scan_result.html',
                success=False,
                message="Book not found in database."
            )

    return render_template('scan.html')


@app.route('/book/<int:book_id>/qr')
def generate_qr_code(book_id):
    """Generate QR code for a book"""
    book = Book.query.get_or_404(book_id)
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(f"{request.host}/book/{book_id}")
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    img_base64 = base64.b64encode(buffer.getvalue()).decode()

    return jsonify({'qr_code': f'data:image/png;base64,{img_base64}'})


# ============== BORROWING SYSTEM ==============

@app.route('/borrow/<int:book_id>', methods=['POST'])
@login_required
def borrow_book(book_id):
    """Borrow a book"""
    book = Book.query.get_or_404(book_id)

    if book.available_copies <= 0:
        flash('This book is not available right now.', 'danger')
        return redirect(url_for('view_book_detail', book_id=book_id))

    # Check if user already has this book
    existing = Borrowing.query.filter_by(
        user_id=current_user.id,
        book_id=book_id,
        returned_at=None
    ).first()

    if existing:
        flash('You already have this book!', 'warning')
        return redirect(url_for('view_book_detail', book_id=book_id))

    # Create borrowing record (14 days loan period)
    due_date = datetime.utcnow() + timedelta(days=14)
    borrowing = Borrowing(
        user_id=current_user.id,
        book_id=book_id,
        due_date=due_date
    )

    book.available_copies -= 1
    if book.available_copies == 0:
        book.status = BookStatus.BORROWED

    db.session.add(borrowing)
    db.session.commit()

    log_activity('borrow', book_id=book_id, details=f'Due: {due_date}')
    create_notification(
        current_user.id,
        'Book Borrowed',
        f'You borrowed "{book.title}". Due date: {due_date.strftime("%d-%m-%Y")}',
        'borrow'
    )

    flash(f'You successfully borrowed "{book.title}"!', 'success')
    return redirect(url_for('view_book_detail', book_id=book_id))


@app.route('/return/<int:borrowing_id>', methods=['POST'])
@login_required
def return_book(borrowing_id):
    """Return a borrowed book"""
    borrowing = Borrowing.query.get_or_404(borrowing_id)

    if borrowing.user_id != current_user.id:
        flash('You cannot return a book you did not borrow!', 'danger')
        return redirect(url_for('dashboard'))

    book = borrowing.book
    borrowing.returned_at = datetime.utcnow()

    # Calculate fine if overdue
    if borrowing.is_overdue():
        borrowing.fine_paid = borrowing.calculate_fine()

    book.available_copies += 1
    if book.status == BookStatus.BORROWED and book.available_copies > 0:
        book.status = BookStatus.AVAILABLE

    db.session.commit()

    log_activity('return', book_id=book.id)
    message = f'You returned "{book.title}"'
    if borrowing.fine_paid > 0:
        message += f' (Fine: ₹{borrowing.fine_paid})'

    flash(message, 'success')
    return redirect(url_for('dashboard'))


@app.route('/reserve/<int:book_id>', methods=['POST'])
@login_required
def reserve_book(book_id):
    """Reserve a book"""
    book = Book.query.get_or_404(book_id)

    existing = Reservation.query.filter_by(
        user_id=current_user.id,
        book_id=book_id,
        is_fulfilled=False,
        canceled_at=None
    ).first()

    if existing:
        flash('You already have a reservation for this book!', 'warning')
        return redirect(url_for('view_book_detail', book_id=book_id))

    # Check if book is available
    if book.available_copies > 0:
        flash('This book is currently available. You can borrow it instead!', 'info')
        return redirect(url_for('view_book_detail', book_id=book_id))

    reservation = Reservation(
        user_id=current_user.id,
        book_id=book_id
    )
    db.session.add(reservation)
    db.session.commit()

    create_notification(
        current_user.id,
        'Reservation Confirmed',
        f'You reserved "{book.title}". You will be notified when it becomes available.',
        'reservation'
    )

    flash(f'Reserve request submitted for "{book.title}"!', 'success')
    return redirect(url_for('view_book_detail', book_id=book_id))


# ============== REVIEW SYSTEM ==============

@app.route('/book/<int:book_id>/review', methods=['POST'])
@login_required
def add_review(book_id):
    """Add or update a book review"""
    book = Book.query.get_or_404(book_id)
    rating = request.form.get('rating', type=int)
    review_text = request.form.get('review_text', '')

    if not 1 <= rating <= 5:
        flash('Rating must be between 1 and 5!', 'danger')
        return redirect(url_for('view_book_detail', book_id=book_id))

    review = Review.query.filter_by(
        user_id=current_user.id,
        book_id=book_id
    ).first()

    if review:
        review.rating = rating
        review.review_text = review_text
        review.updated_at = datetime.utcnow()
    else:
        review = Review(
            user_id=current_user.id,
            book_id=book_id,
            rating=rating,
            review_text=review_text
        )
        db.session.add(review)

    # Update book's average rating
    all_reviews = Review.query.filter_by(book_id=book_id).all()
    avg_rating = sum(r.rating for r in all_reviews) / len(all_reviews)
    book.average_rating = round(avg_rating, 2)

    db.session.commit()
    flash('Review posted successfully!', 'success')
    return redirect(url_for('view_book_detail', book_id=book_id))


# ============== NOTIFICATION SYSTEM ==============

@app.route('/notifications')
@login_required
def get_notifications():
    """Get user's notifications"""
    page = request.args.get('page', 1, type=int)
    notifications = Notification.query.filter_by(
        user_id=current_user.id
    ).order_by(Notification.created_at.desc()).paginate(page=page, per_page=20)

    return render_template('notifications.html', notifications=notifications)


@app.route('/notification/<int:notification_id>/read', methods=['POST'])
@login_required
def mark_notification_read(notification_id):
    """Mark notification as read"""
    notification = Notification.query.get_or_404(notification_id)
    if notification.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    notification.is_read = True
    db.session.commit()
    return jsonify({'status': 'success'})


# ============== API ENDPOINTS FOR REAL-TIME UPDATES ==============

@app.route('/api/book/<int:book_id>/status')
@login_required
def get_book_status(book_id):
    """Get real-time book status"""
    book = Book.query.get_or_404(book_id)
    current_borrower = book.get_current_borrower()

    return jsonify({
        'book_id': book.id,
        'title': book.title,
        'status': book.status.value,
        'available_copies': book.available_copies,
        'total_copies': book.total_copies,
        'current_borrower': current_borrower.full_name if current_borrower else None,
        'is_available': book.is_available()
    })


@app.route('/api/user/borrowings')
@login_required
def get_user_borrowings():
    """Get user's active borrowings"""
    borrowings = current_user.get_active_borrowings()
    data = []
    for b in borrowings:
        data.append({
            'borrowing_id': b.id,
            'book_title': b.book.title,
            'borrowed_at': b.borrowed_at.isoformat(),
            'due_date': b.due_date.isoformat(),
            'is_overdue': b.is_overdue(),
            'days_overdue': b.get_days_overdue(),
            'fine': b.calculate_fine()
        })
    return jsonify(data)


@app.route('/api/stats')
def get_stats():
    """Get library statistics"""
    return jsonify({
        'total_books': Book.query.count(),
        'available_books': Book.query.filter_by(status=BookStatus.AVAILABLE).count(),
        'total_members': User.query.filter_by(role=UserRole.STUDENT).count(),
        'active_borrowings': Borrowing.query.filter_by(returned_at=None).count(),
        'timestamp': datetime.utcnow().isoformat()
    })


# ============== WEBSOCKET EVENTS ==============

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    if current_user.is_authenticated:
        join_room(f'user_{current_user.id}')
        emit('connected', {'message': 'Connected to real-time updates'})


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    if current_user.is_authenticated:
        leave_room(f'user_{current_user.id}')


@socketio.on('get_updates')
def handle_get_updates():
    """Send real-time updates"""
    if current_user.is_authenticated:
        borrowings = current_user.get_active_borrowings()
        emit('updates', {
            'active_borrowings': len(borrowings),
            'overdue_count': sum(1 for b in borrowings if b.is_overdue()),
            'timestamp': datetime.utcnow().isoformat()
        })


# ============== ERROR HANDLERS ==============

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(e):
    db.session.rollback()
    return render_template('500.html'), 500


# ============== CREATE DATABASE & RUN ==============

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("Database initialized!")
    
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
