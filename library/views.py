"""Views for the library app."""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods, require_POST
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Q, Avg
from datetime import timedelta

# Optional: OpenCV and pyzbar for barcode scanning (not available in all environments)
try:
    import cv2
    from pyzbar.pyzbar import decode
    BARCODE_SCANNING_AVAILABLE = True
except ImportError:
    BARCODE_SCANNING_AVAILABLE = False
    cv2 = None
    decode = None

import qrcode
from io import BytesIO
import base64
import json
from functools import wraps

from .models import (
    User, Book, Borrowing, Reservation, Review, ActivityLog, Notification, UserRole, BookStatus
)
from .forms import UserRegistrationForm, UserLoginForm, BookForm, ReviewForm
from .utils import log_activity, create_notification


def librarian_required(view_func):
    """Decorator for librarian-only views."""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role == UserRole.STUDENT:
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('index')
        return view_func(request, *args, **kwargs)
    return wrapper


# ============== AUTHENTICATION VIEWS ==============

def register(request):
    """User registration view."""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            log_activity(request, 'Registration successful', user=user)
            messages.success(request, 'Registration successful! Please login.')
            return redirect('login')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = UserRegistrationForm()

    return render(request, 'register.html', {'form': form})


def login_view(request):
    """User login view."""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)

            if user is not None:
                if not user.is_active:
                    messages.error(request, 'Your account has been deactivated.')
                    return redirect('login')

                login(request, user)
                log_activity(request, 'login', user=user)
                messages.success(request, f'Welcome back, {user.first_name}!')
                return redirect('dashboard')
            else:
                messages.error(request, 'Invalid username or password!')
    else:
        form = UserLoginForm()

    return render(request, 'login.html', {'form': form})


@require_POST
@login_required
def logout_view(request):
    """User logout view."""
    log_activity(request, 'logout', user=request.user)
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('index')


# ============== MAIN VIEWS ==============

def index(request):
    """Home/Landing page."""
    if request.user.is_authenticated:
        return redirect('dashboard')

    book_count = Book.objects.count()
    user_count = User.objects.filter(role=UserRole.STUDENT).count()
    total_borrowed = Borrowing.objects.filter(returned_at__isnull=True).count()

    context = {
        'book_count': book_count,
        'user_count': user_count,
        'total_borrowed': total_borrowed,
    }
    return render(request, 'index.html', context)


@login_required
def dashboard(request):
    """User dashboard with personalized data."""
    if request.user.role in [UserRole.LIBRARIAN, UserRole.ADMIN]:
        # Librarian dashboard
        total_books = Book.objects.count()
        available_books = Book.objects.filter(status=BookStatus.AVAILABLE).count()
        total_members = User.objects.filter(role=UserRole.STUDENT).count()
        active_borrowings = Borrowing.objects.filter(returned_at__isnull=True).count()
        overdue_count = sum(1 for b in Borrowing.objects.filter(returned_at__isnull=True) if b.is_overdue())

        # Recent activities
        recent_activities = ActivityLog.objects.order_by('-timestamp')[:10]

        context = {
            'total_books': total_books,
            'available_books': available_books,
            'total_members': total_members,
            'active_borrowings': active_borrowings,
            'overdue_count': overdue_count,
            'recent_activities': recent_activities,
        }
        return render(request, 'librarian_dashboard.html', context)
    else:
        # Student dashboard
        active_borrowings = request.user.get_active_borrowings()
        overdue_count = sum(1 for b in active_borrowings if b.is_overdue())
        total_fine = sum(b.calculate_fine() for b in active_borrowings if b.is_overdue())

        notifications = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).order_by('-created_at')

        context = {
            'active_borrowings': active_borrowings,
            'overdue_count': overdue_count,
            'total_fine': total_fine,
            'notifications': notifications,
        }
        return render(request, 'student_dashboard.html', context)


# ============== BOOK MANAGEMENT VIEWS ==============

@login_required
def view_books(request):
    """View all books with search and filter."""
    page_num = request.GET.get('page', 1)
    search_query = request.GET.get('q', '')
    genre_filter = request.GET.get('genre', '')
    status_filter = request.GET.get('status', '')

    books_query = Book.objects.all()

    if search_query:
        books_query = books_query.filter(
            Q(title__icontains=search_query) |
            Q(author__icontains=search_query) |
            Q(isbn__icontains=search_query)
        )
        log_activity(request, 'search', details=f'Searched: {search_query}')

    if genre_filter:
        books_query = books_query.filter(genre=genre_filter)

    if status_filter and request.user.role in [UserRole.LIBRARIAN, UserRole.ADMIN]:
        books_query = books_query.filter(status=status_filter)

    # Pagination
    paginator = Paginator(books_query, 12)
    books = paginator.get_page(page_num)

    # Get distinct genres
    genres = Book.objects.values_list('genre', flat=True).distinct()

    context = {
        'books': books,
        'genres': genres,
        'search_query': search_query,
        'genre_filter': genre_filter,
    }
    return render(request, 'list_books.html', context)


@login_required
def view_book_detail(request, book_id):
    """View book details and reviews."""
    book = get_object_or_404(Book, pk=book_id)
    reviews = Review.objects.filter(book=book).order_by('-created_at')
    user_review = None

    if request.user.is_authenticated:
        user_review = Review.objects.filter(book=book, user=request.user).first()

    log_activity(request, 'view_book', book=book)

    context = {
        'book': book,
        'reviews': reviews,
        'user_review': user_review,
        'review_form': ReviewForm(),
    }
    return render(request, 'book_detail.html', context)


@login_required
@librarian_required
def add_book(request):
    """Add a new book (Librarian only)."""
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            book = form.save()
            log_activity(request, 'add_book', book=book)
            messages.success(request, f'Book "{book.title}" added successfully!')
            return redirect('view_book_detail', book_id=book.id)
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = BookForm()

    return render(request, 'add_book.html', {'form': form})


@login_required
@librarian_required
def edit_book(request, book_id):
    """Edit book details."""
    book = get_object_or_404(Book, pk=book_id)

    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES, instance=book)
        if form.is_valid():
            book = form.save()
            log_activity(request, 'edit_book', book=book)
            messages.success(request, 'Book updated successfully!')
            return redirect('view_book_detail', book_id=book.id)
    else:
        form = BookForm(instance=book)

    return render(request, 'edit_book.html', {'form': form, 'book': book})


@require_POST
@login_required
@librarian_required
def delete_book(request, book_id):
    """Delete a book."""
    book = get_object_or_404(Book, pk=book_id)
    title = book.title
    book.delete()

    log_activity(request, 'delete_book', details=f'Deleted: {title}')
    messages.success(request, f'Book "{title}" deleted successfully!')
    return redirect('view_books')


# ============== BARCODE & QR CODE VIEWS ==============

@login_required
def scan_book(request):
    """Barcode scanning page."""
    if not BARCODE_SCANNING_AVAILABLE:
        return render(request, 'scan.html', {
            'error': 'Barcode scanning is not available. Required libraries (OpenCV, pyzbar) are not installed. '
                     'Please use QR code scanning or manual ISBN entry instead.'
        })
    
    if request.method == 'POST':
        rack_no = request.POST.get('rack_no')
        if not rack_no:
            return render(request, 'scan.html', {'error': 'Please enter a rack number.'})

        # Initialize camera
        cap = cv2.VideoCapture(0)
        scanned_data = None

        try:
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
        finally:
            cap.release()
            cv2.destroyAllWindows()

        if not scanned_data:
            return render(request, 'scan.html', {'error': 'No barcode detected. Try again.'})

        book = Book.objects.filter(barcode=scanned_data).first()
        if book:
            if book.rack_no == rack_no:
                recommendations = Book.objects.filter(
                    genre=book.genre,
                    status=BookStatus.AVAILABLE
                ).exclude(id=book.id)[:3]

                log_activity(request, 'scan_success', book=book)
                return render(request, 'scan_result.html', {
                    'success': True,
                    'message': f"✓ '{book.title}' is in the correct rack!",
                    'book': book,
                    'recommendations': recommendations,
                })
            else:
                log_activity(request, 'scan_misplaced', book=book)
                return render(request, 'scan_result.html', {
                    'success': False,
                    'message': f"✗ '{book.title}' is in the wrong rack. Should be in rack {book.rack_no}",
                    'book': book,
                })
        else:
            return render(request, 'scan_result.html', {
                'success': False,
                'message': 'Book not found in database.',
            })

    return render(request, 'scan.html')


@login_required
def generate_qr_code(request, book_id):
    """Generate QR code for a book."""
    book = get_object_or_404(Book, pk=book_id)

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(f"{request.build_absolute_uri('/book/' + str(book_id) + '/')}")
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    # Convert to base64
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    img_base64 = base64.b64encode(buffer.getvalue()).decode()

    return JsonResponse({'qr_code': f'data:image/png;base64,{img_base64}'})


# ============== BORROWING SYSTEM ==============

@require_POST
@login_required
def borrow_book(request, book_id):
    """Borrow a book."""
    book = get_object_or_404(Book, pk=book_id)

    if book.available_copies <= 0:
        messages.error(request, 'This book is not available right now.')
        return redirect('view_book_detail', book_id=book_id)

    # Check if user already has this book
    existing = Borrowing.objects.filter(
        user=request.user,
        book=book,
        returned_at__isnull=True
    ).first()

    if existing:
        messages.warning(request, 'You already have this book!')
        return redirect('view_book_detail', book_id=book_id)

    # Create borrowing record (14 days loan period)
    due_date = timezone.now() + timedelta(days=14)
    borrowing = Borrowing.objects.create(
        user=request.user,
        book=book,
        due_date=due_date
    )

    book.available_copies -= 1
    if book.available_copies == 0:
        book.status = BookStatus.BORROWED
    book.save()

    log_activity(request, 'borrow', book=book, details=f'Due: {due_date}')
    create_notification(
        request.user,
        'Book Borrowed',
        f'You borrowed "{book.title}". Due date: {due_date.strftime("%d-%m-%Y")}',
        'borrow'
    )

    messages.success(request, f'You successfully borrowed "{book.title}"!')
    return redirect('view_book_detail', book_id=book_id)


@require_POST
@login_required
def return_book(request, borrowing_id):
    """Return a borrowed book."""
    borrowing = get_object_or_404(Borrowing, pk=borrowing_id)

    if borrowing.user != request.user:
        messages.error(request, 'You cannot return a book you did not borrow!')
        return redirect('dashboard')

    book = borrowing.book
    borrowing.returned_at = timezone.now()

    # Calculate fine if overdue
    if borrowing.is_overdue():
        borrowing.fine_paid = borrowing.calculate_fine()

    borrowing.save()

    book.available_copies += 1
    if book.status == BookStatus.BORROWED and book.available_copies > 0:
        book.status = BookStatus.AVAILABLE
    book.save()

    log_activity(request, 'return', book=book)
    message = f'You returned "{book.title}"'
    if borrowing.fine_paid > 0:
        message += f' (Fine: ₹{borrowing.fine_paid})'

    messages.success(request, message)
    return redirect('dashboard')


@require_POST
@login_required
def reserve_book(request, book_id):
    """Reserve a book."""
    book = get_object_or_404(Book, pk=book_id)

    existing = Reservation.objects.filter(
        user=request.user,
        book=book,
        is_fulfilled=False,
        canceled_at__isnull=True
    ).first()

    if existing:
        messages.warning(request, 'You already have a reservation for this book!')
        return redirect('view_book_detail', book_id=book_id)

    # Check if book is available
    if book.available_copies > 0:
        messages.info(request, 'This book is currently available. You can borrow it instead!')
        return redirect('view_book_detail', book_id=book_id)

    reservation = Reservation.objects.create(
        user=request.user,
        book=book
    )

    create_notification(
        request.user,
        'Reservation Confirmed',
        f'You reserved "{book.title}". You will be notified when it becomes available.',
        'reservation'
    )

    messages.success(request, f'Reserve request submitted for "{book.title}"!')
    return redirect('view_book_detail', book_id=book_id)


# ============== REVIEW SYSTEM ==============

@require_POST
@login_required
def add_review(request, book_id):
    """Add or update a book review."""
    book = get_object_or_404(Book, pk=book_id)
    form = ReviewForm(request.POST)

    if form.is_valid():
        rating = form.cleaned_data['rating']
        review_text = form.cleaned_data['review_text']

        review, created = Review.objects.update_or_create(
            user=request.user,
            book=book,
            defaults={
                'rating': rating,
                'review_text': review_text,
            }
        )

        # Update book's average rating
        avg_rating = Review.objects.filter(book=book).aggregate(Avg('rating'))['rating__avg'] or 0
        book.average_rating = round(avg_rating, 2)
        book.save()

        messages.success(request, 'Review posted successfully!')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(request, f'{field}: {error}')

    return redirect('view_book_detail', book_id=book_id)


# ============== NOTIFICATION SYSTEM ==============

@login_required
def get_notifications(request):
    """Get user's notifications."""
    page_num = request.GET.get('page', 1)
    notifications_query = Notification.objects.filter(user=request.user).order_by('-created_at')

    paginator = Paginator(notifications_query, 20)
    notifications = paginator.get_page(page_num)

    return render(request, 'notifications.html', {'notifications': notifications})


@require_POST
@login_required
def mark_notification_read(request, notification_id):
    """Mark notification as read."""
    notification = get_object_or_404(Notification, pk=notification_id)

    if notification.user != request.user:
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    notification.is_read = True
    notification.save()

    return JsonResponse({'status': 'success'})


# ============== API ENDPOINTS FOR REAL-TIME UPDATES ==============

@login_required
def get_book_status(request, book_id):
    """Get real-time book status."""
    book = get_object_or_404(Book, pk=book_id)
    current_borrower = book.get_current_borrower()

    return JsonResponse({
        'book_id': book.id,
        'title': book.title,
        'status': book.status,
        'available_copies': book.available_copies,
        'total_copies': book.total_copies,
        'current_borrower': current_borrower.get_full_name() if current_borrower else None,
        'is_available': book.is_available(),
    })


@login_required
def get_user_borrowings(request):
    """Get user's active borrowings."""
    borrowings = request.user.get_active_borrowings()
    data = []
    for b in borrowings:
        data.append({
            'borrowing_id': b.id,
            'book_title': b.book.title,
            'borrowed_at': b.borrowed_at.isoformat(),
            'due_date': b.due_date.isoformat(),
            'is_overdue': b.is_overdue(),
            'days_overdue': b.get_days_overdue(),
            'fine': b.calculate_fine(),
        })
    return JsonResponse(data, safe=False)


def get_stats(request):
    """Get library statistics."""
    return JsonResponse({
        'total_books': Book.objects.count(),
        'available_books': Book.objects.filter(status=BookStatus.AVAILABLE).count(),
        'total_members': User.objects.filter(role=UserRole.STUDENT).count(),
        'active_borrowings': Borrowing.objects.filter(returned_at__isnull=True).count(),
        'timestamp': timezone.now().isoformat(),
    })


# ============== ERROR HANDLERS ==============

def page_not_found(request, exception):
    """404 error handler."""
    return render(request, '404.html', status=404)


def server_error(request):
    """500 error handler."""
    return render(request, '500.html', status=500)
