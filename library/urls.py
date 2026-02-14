"""URL configuration for library app."""
from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Main pages
    path('', views.index, name='index'),
    path('dashboard/', views.dashboard, name='dashboard'),

    # Book management
    path('books/', views.view_books, name='view_books'),
    path('book/<int:book_id>/', views.view_book_detail, name='view_book_detail'),
    path('add-book/', views.add_book, name='add_book'),
    path('edit/<int:book_id>/', views.edit_book, name='edit_book'),
    path('delete/<int:book_id>/', views.delete_book, name='delete_book'),

    # Barcode & QR code
    path('scan/', views.scan_book, name='scan_book'),
    path('book/<int:book_id>/qr/', views.generate_qr_code, name='generate_qr'),

    # Borrowing system
    path('borrow/<int:book_id>/', views.borrow_book, name='borrow_book'),
    path('return/<int:borrowing_id>/', views.return_book, name='return_book'),
    path('reserve/<int:book_id>/', views.reserve_book, name='reserve_book'),

    # Reviews
    path('book/<int:book_id>/review/', views.add_review, name='add_review'),

    # Notifications
    path('notifications/', views.get_notifications, name='get_notifications'),
    path('notification/<int:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),

    # API endpoints
    path('api/book/<int:book_id>/status/', views.get_book_status, name='get_book_status'),
    path('api/user/borrowings/', views.get_user_borrowings, name='get_user_borrowings'),
    path('api/stats/', views.get_stats, name='get_stats'),
]
