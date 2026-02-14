// SmartLib - Main JavaScript File

// Initialize Socket.IO for real-time updates
const socket = io();

// Connect to socket
socket.on('connect', function() {
    console.log('Connected to server');
    socket.emit('get_updates');
});

// Handle real-time notifications
socket.on('notification', function(data) {
    showNotification(data.title, data.message, data.type);
    updateNotificationBadge();
});

// Handle real-time updates
socket.on('updates', function(data) {
    console.log('Received updates:', data);
    updateDashboard(data);
});

// Show notification toast
function showNotification(title, message, type = 'info') {
    const alertClass = {
        'success': 'alert-success',
        'danger': 'alert-danger',
        'warning': 'alert-warning',
        'info': 'alert-info',
        'overdue': 'alert-danger',
        'available': 'alert-success',
        'reminder': 'alert-warning',
        'borrow': 'alert-info',
        'reservation': 'alert-info'
    }[type] || 'alert-info';

    const alertHTML = `
        <div class="alert ${alertClass} alert-dismissible fade show" role="alert" style="position: fixed; top: 80px; right: 20px; z-index: 9999; max-width: 400px;">
            <strong>${title}</strong><br>${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', alertHTML);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        const alerts = document.querySelectorAll('.alert[role="alert"]');
        alerts.forEach(a => a.remove());
    }, 5000);
}

// Update notification badge
function updateNotificationBadge() {
    fetch('/api/user/borrowings')
        .then(response => response.json())
        .then(borrowings => {
            const overdueCount = borrowings.filter(b => b.is_overdue).length;
            const badge = document.querySelector('.notification-badge');
            if (badge) {
                if (overdueCount > 0) {
                    badge.classList.remove('d-none');
                    badge.textContent = overdueCount;
                } else {
                    badge.classList.add('d-none');
                }
            }
        });
}

// Update dashboard with real-time data
function updateDashboard(data) {
    // This can be customized based on dashboard needs
    console.log('Dashboard updated:', data);
}

// Format date
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-IN', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

// Format currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR'
    }).format(amount);
}

// Search with debouncing
let searchTimeout;
function debounceSearch(fn, delay = 300) {
    return function(...args) {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => fn(...args), delay);
    };
}

// Book search functionality
const bookSearch = debounceSearch(function(query) {
    if (query.trim() === '') {
        loadBooks();
        return;
    }

    fetch(`/books?q=${encodeURIComponent(query)}`)
        .then(response => response.text())
        .then(html => {
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');
            const booksContainer = document.querySelector('.books-container');
            if (booksContainer) {
                booksContainer.innerHTML = doc.querySelector('.books-container').innerHTML;
            }
        });
});

// Load books
function loadBooks() {
    fetch('/books')
        .then(response => response.text())
        .then(html => {
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');
            const booksContainer = document.querySelector('.books-container');
            if (booksContainer) {
                booksContainer.innerHTML = doc.querySelector('.books-container').innerHTML;
            }
        });
}

// Confirm action with SweetAlert-like confirmation
function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

// Copy to clipboard
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showNotification('Copied', 'Text copied to clipboard', 'success');
    }).catch(err => {
        console.error('Failed to copy:', err);
    });
}

// Toggle dark mode
function toggleDarkMode() {
    document.body.classList.toggle('dark-mode');
    localStorage.setItem('darkMode', document.body.classList.contains('dark-mode'));
}

// Load dark mode preference
function loadDarkModePreference() {
    if (localStorage.getItem('darkMode') === 'true') {
        document.body.classList.add('dark-mode');
    }
}

// Get book status in real-time
function getBookStatus(bookId) {
    return fetch(`/api/book/${bookId}/status`)
        .then(response => response.json())
        .catch(err => console.error('Error fetching book status:', err));
}

// Get user's borrowings
function getUserBorrowings() {
    return fetch('/api/user/borrowings')
        .then(response => response.json())
        .catch(err => console.error('Error fetching borrowings:', err));
}

// Get library statistics
function getLibraryStats() {
    return fetch('/api/stats')
        .then(response => response.json())
        .catch(err => console.error('Error fetching stats:', err));
}

// Format time remaining
function getTimeRemaining(dueDate) {
    const now = new Date();
    const due = new Date(dueDate);
    const diff = due - now;
    
    if (diff < 0) {
        const days = Math.ceil(Math.abs(diff) / (1000 * 60 * 60 * 24));
        return `${days} day${days > 1 ? 's' : ''} overdue`;
    }
    
    const days = Math.ceil(diff / (1000 * 60 * 60 * 24));
    return `${days} day${days > 1 ? 's' : ''} remaining`;
}

// Validate forms
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return true;

    const inputs = form.querySelectorAll('[required]');
    let isValid = true;

    inputs.forEach(input => {
        if (!input.value.trim()) {
            input.classList.add('is-invalid');
            isValid = false;
        } else {
            input.classList.remove('is-invalid');
        }
    });

    return isValid;
}

// Initialize tooltips (Bootstrap)
function initializeTooltips() {
    // Initialize Bootstrap tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Initialize popovers (Bootstrap)
function initializePopovers() {
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
}

// Smooth scroll
function smoothScroll(target) {
    document.querySelector(target).scrollIntoView({
        behavior: 'smooth'
    });
}

// Handle QR code generation
function generateQRCode(bookId) {
    fetch(`/book/${bookId}/qr`)
        .then(response => response.json())
        .then(data => {
            const qrModal = new bootstrap.Modal(document.getElementById('qrModal'));
            document.getElementById('qrImage').src = data.qr_code;
            qrModal.show();
        })
        .catch(err => {
            showNotification('Error', 'Failed to generate QR code', 'danger');
            console.error('QR generation error:', err);
        });
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    loadDarkModePreference();
    initializeTooltips();
    initializePopovers();
    updateNotificationBadge();

    // Setup event listeners
    const searchInput = document.getElementById('searchBooks');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            bookSearch(this.value);
        });
    }

    // Update notification badge every 30 seconds
    setInterval(updateNotificationBadge, 30000);
});

// Export functions for use in templates
window.SmartLib = {
    showNotification,
    getBookStatus,
    getUserBorrowings,
    getLibraryStats,
    getTimeRemaining,
    generateQRCode,
    toggleDarkMode,
    copyToClipboard,
    smoothScroll
};
