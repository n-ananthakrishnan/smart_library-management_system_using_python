"""Registry and admin configuration for models."""
from django.contrib import admin
from django.utils.html import format_html
from .models import User, Book, Borrowing, Reservation, Review, ActivityLog, Notification


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'get_full_name_display', 'role', 'is_active', 'created_at')
    list_filter = ('role', 'is_active', 'created_at')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    readonly_fields = ('created_at', 'updated_at')

    def get_full_name_display(self, obj):
        """Display user's full name or username if not available"""
        full_name = obj.get_full_name()
        return full_name if full_name.strip() else obj.username
    get_full_name_display.short_description = 'Full Name'


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'isbn', 'status_badge', 'available_copies', 'total_copies', 'added_at')
    list_filter = ('status', 'genre', 'added_at')
    search_fields = ('title', 'author', 'isbn', 'barcode')
    readonly_fields = ('added_at', 'updated_at')

    def status_badge(self, obj):
        colors = {
            'available': '#28a745',
            'borrowed': '#ffc107',
            'reserved': '#17a2b8',
            'lost': '#dc3545',
            'maintenance': '#6c757d',
        }
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            colors.get(obj.status, '#000'),
            obj.get_status_display(),
        )
    status_badge.short_description = 'Status'


@admin.register(Borrowing)
class BorrowingAdmin(admin.ModelAdmin):
    list_display = ('user', 'book', 'borrowed_at', 'due_date', 'is_overdue_badge', 'returned_at')
    list_filter = ('borrowed_at', 'returned_at')
    search_fields = ('user__username', 'book__title')
    readonly_fields = ('borrowed_at',)

    def is_overdue_badge(self, obj):
        if obj.is_overdue():
            return format_html(
                '<span style="color: red; font-weight: bold;">OVERDUE ({} days)</span>',
                obj.get_days_overdue()
            )
        return format_html('<span style="color: green;">On time</span>')
    is_overdue_badge.short_description = 'Overdue Status'


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('user', 'book', 'reserved_at', 'is_fulfilled', 'fulfilled_at')
    list_filter = ('is_fulfilled', 'reserved_at')
    search_fields = ('user__username', 'book__title')
    readonly_fields = ('reserved_at',)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'book', 'rating_display', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('user__username', 'book__title')
    readonly_fields = ('created_at', 'updated_at')

    def rating_display(self, obj):
        return '⭐' * obj.rating
    rating_display.short_description = 'Rating'


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('action', 'user', 'book', 'timestamp', 'ip_address')
    list_filter = ('action', 'timestamp')
    search_fields = ('user__username', 'book__title')
    readonly_fields = ('timestamp',)
    date_hierarchy = 'timestamp'


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'type', 'is_read', 'created_at')
    list_filter = ('type', 'is_read', 'created_at')
    search_fields = ('user__username', 'title')
    readonly_fields = ('created_at',)
