# API Documentation

Complete API reference for the Smart Library Management System.

## Table of Contents
- [Authentication](#authentication)
- [Books API](#books-api)
- [User API](#user-api)
- [Borrowing API](#borrowing-api)
- [Review API](#review-api)
- [Notification API](#notification-api)
- [WebSocket Events](#websocket-events)
- [Error Handling](#error-handling)

## Authentication

### Register User
```http
POST /register
```

**Content-Type**: `application/x-www-form-urlencoded`

**Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| full_name | string | Yes | User's full name |
| email | string | Yes | Valid email address |
| username | string | Yes | Unique username (3-20 chars) |
| password | string | Yes | Password (min 6 chars) |
| confirm_password | string | Yes | Password confirmation (must match) |
| roll_number | string | No | Student/Member ID |

**Response** (302 Redirect to login):
```bash
Redirects to /login on success
```

**Error Responses**:
```json
{
  "message": "Username already exists",
  "alert_type": "danger"
}
```

### Login
```http
POST /login
Content-Type: application/x-www-form-urlencoded

username=user&password=pass123&remember=on
```

**Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| username | string | Yes | Username or email |
| password | string | Yes | Password |
| remember | boolean | No | Remember login (creates persistent cookie) |

**Response** (302 Redirect):
```bash
Redirects to /dashboard on success
```

### Logout
```http
GET /logout
```

**Authentication**: Required

**Response** (302 Redirect):
```bash
Redirects to / (home page)
```

**Session**: Clears user session cookie

---

## Books API

### Get All Books
```http
GET /books
```

**Query Parameters**:
| Name | Type | Default | Description |
|------|------|---------|-------------|
| page | integer | 1 | Page number for pagination |
| genre | string | - | Filter by genre |
| search | string | - | Search in title/author |
| per_page | integer | 12 | Items per page |

**Response** (200 OK):
```html
HTML Page with book cards
Books paginated, filtered by genre/search
```

**Example**:
```bash
GET /books?page=1&genre=Fiction&search=Harry
```

### Get Book Details
```http
GET /book/<book_id>
```

**Parameters**:
| Name | Type | Description |
|------|------|-------------|
| book_id | integer | Book ID |

**Response** (200 OK):
```html
Book detail page with:
- Book metadata
- Availability status
- QR code option
- Reviews and ratings
- Borrow/Reserve buttons
```

### Add Book (Librarian Only)
```http
POST /add-book
Content-Type: application/x-www-form-urlencoded
```

**Authentication**: Required (Librarian role)

**Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| title | string | Yes | Book title |
| author | string | Yes | Author name |
| isbn | string | Yes | ISBN (unique) |
| barcode | string | Yes | Barcode (unique) |
| genre | string | Yes | Genre |
| category | string | No | Category |
| rack_no | string | Yes | Rack location |
| shelf_no | string | No | Shelf location |
| edition | string | No | Edition |
| publication_year | integer | No | Year of publication |
| publisher | string | No | Publisher name |
| pages | integer | No | Number of pages |
| total_copies | integer | No | Total copies (default: 1) |
| description | text | No | Book description |

**Response** (302 Redirect):
```bash
Redirects to /books on success
Flash message: "Book added successfully"
```

**Error Responses** (400 Bad Request):
```json
{
  "message": "ISBN already exists",
  "alert_type": "danger"
}
```

### Edit Book (Librarian Only)
```http
POST /edit-book/<book_id>
Content-Type: application/x-www-form-urlencoded
```

**Authentication**: Required (Librarian role)

**Parameters**: Same as Add Book

**Response** (302 Redirect):
```bash
Redirects to /book/<book_id> on success
```

### Delete Book (Librarian Only)
```http
POST /delete-book/<book_id>
```

**Authentication**: Required (Librarian role)

**Response** (302 Redirect):
```bash
Redirects to /books on success
Flash message: "Book deleted successfully"
```

---

## User API

### Get Dashboard
```http
GET /dashboard
```

**Authentication**: Required

**Response** (200 OK):
```html
User dashboard:
- For Students: Active borrowings, upcoming dues, notifications
- For Librarians: Statistics, activity log, analytics
```

### Get Librarian Dashboard
```http
GET /librarian-dashboard
```

**Authentication**: Required (Librarian role)

**Response** (200 OK):
```html
Analytics dashboard with:
- Total books count
- Available books
- Active borrowings
- Overdue books
- Total members
- Recent activities timeline
```

---

## Borrowing API

### Borrow Book
```http
POST /borrow-book/<book_id>
```

**Authentication**: Required (Student role)

**Parameters**: None (book_id in URL)

**Response** (302 Redirect):
```bash
Redirects to /books on success
Flash message: "Book borrowed successfully"
Notification: Real-time notification via WebSocket
```

**Error Responses**:
```json
{
  "message": "Book is not available",
  "alert_type": "danger"
}
```

**Rules**:
- Book must have available copies
- User cannot exceed 5 active borrowings
- Borrowing duration: 14 days (customizable)
- Fine: $0.50/day overdue

### Return Book
```http
POST /return-book/<borrowing_id>
```

**Authentication**: Required (Student role)

**Response** (302 Redirect):
```bash
Redirects to /dashboard on success
Flash message: "Book returned successfully"
Notification: Real-time update via WebSocket
```

**Auto-Calculated**:
- Fine if overdue: (days_overdue × $0.50)
- Activity logged for audit trail

### Reserve Book
```http
POST /reserve-book/<book_id>
```

**Authentication**: Required (Student role)

**Response** (302 Redirect):
```bash
Redirects to /book/<book_id> on success
Flash message: "Book reserved successfully"
```

**Rules**:
- Only for unavailable books
- Max 1 reservation per user per book
- Auto-notification when available
- 7-day hold period

---

## Review API

### Add/Update Review
```http
POST /add-review/<book_id>
Content-Type: application/x-www-form-urlencoded
```

**Authentication**: Required

**Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| rating | integer | Yes | Rating (1-5 stars) |
| text | string | No | Review text |

**Response** (302 Redirect):
```bash
Redirects to /book/<book_id> on success
```

**Response Body**:
```html
Renders book detail page with updated review
```

**Rules**:
- User must have borrowed the book
- Updates existing review if present
- Average rating auto-calculated across all reviews

---

## Notification API

### Get Notifications
```http
GET /notifications
```

**Authentication**: Required

**Query Parameters**:
| Name | Type | Default | Description |
|------|------|---------|-------------|
| page | integer | 1 | Page number |
| type | string | - | Filter by type |
| per_page | integer | 20 | Items per page |

**Response** (200 OK):
```html
Notification list with:
- Notification cards by type
- Mark as read buttons
- Pagination controls
- Settings sidebar
```

**Notification Types**:
- `overdue` - Overdue reminder
- `available` - Reserved book available
- `reminder` - Upcoming due date
- `borrow` - Borrowing confirmation
- `reservation` - Reservation confirmation
- `info` - System announcements

### Mark Notification as Read
```http
POST /mark-notification/<notification_id>
```

**Authentication**: Required

**Response** (200 JSON):
```json
{
  "success": true,
  "message": "Marked as read"
}
```

---

## WebSocket Events

### Connection
```javascript
// Client-side
socket.on('connect', function() {
    console.log('Connected to server');
});

// Server response
// - Joins user-specific room: user_{user_id}
// - Ready to receive real-time updates
```

### Receive Notification
```javascript
socket.on('notification', function(data) {
    console.log(data);
    // Data structure:
    // {
    //   'title': 'Book Available',
    //   'message': 'Harry Potter is now available',
    //   'type': 'available'
    // }
});
```

**Auto-Triggered For**:
- New borrowing confirmation
- Book becomes available (if reserved)
- Overdue reminder (24 hours before due)
- Book actually becomes overdue
- System announcements

### Request Dashboard Updates
```javascript
socket.emit('get_updates', {}, function(data) {
    console.log('Dashboard data:', data);
    // Returns current user's borrowing stats
    // and library statistics
});

// Server response
socket.on('updates', function(data) {
    // {
    //   'active_borrowings': [...],
    //   'overdue_count': 2,
    //   'total_books': 500,
    //   'available_books': 350
    // }
});
```

### Disconnect
```javascript
socket.on('disconnect', function() {
    console.log('Disconnected from server');
    // Automatically leaves user room
});
```

---

## REST API Endpoints

### Get Book Status
```http
GET /api/book/<book_id>/status
```

**Response** (200 OK):
```json
{
  "id": 1,
  "title": "Python Programming",
  "available": true,
  "copies_available": 2,
  "total_copies": 5,
  "borrowed_by": null,
  "due_date": null
}
```

### Get User Borrowings
```http
GET /api/user/borrowings
```

**Authentication**: Required

**Response** (200 OK):
```json
{
  "borrowings": [
    {
      "id": 1,
      "book_id": 5,
      "title": "Clean Code",
      "author": "Robert Martin",
      "borrowed_date": "2024-01-15",
      "due_date": "2024-01-29",
      "is_overdue": false,
      "days_remaining": 5,
      "fine": 0
    }
  ],
  "total": 3,
  "overdue_count": 1,
  "total_fine": 5.50
}
```

### Get Statistics
```http
GET /api/stats
```

**Authentication**: Required (Librarian role)

**Response** (200 OK):
```json
{
  "total_books": 1000,
  "available_books": 650,
  "total_members": 250,
  "active_borrowings": 350,
  "overdue_books": 25,
  "total_fine_pending": 125.50,
  "books_by_genre": {
    "Fiction": 300,
    "Science": 250,
    "History": 200
  },
  "monthly_activity": {
    "borrows": 450,
    "returns": 425,
    "new_members": 15
  }
}
```

---

## Error Handling

### HTTP Status Codes
| Code | Meaning | Example |
|------|---------|---------|
| 200 | OK | Successful request |
| 201 | Created | New resource created |
| 302 | Redirect | Redirected to another page |
| 400 | Bad Request | Invalid parameters |
| 401 | Unauthorized | Not authenticated |
| 403 | Forbidden | No permission |
| 404 | Not Found | Resource doesn't exist |
| 500 | Server Error | Internal error |

### Error Response Format
```json
{
  "error": "Error message",
  "message": "User-friendly message"
}
```

### Flash Messages
Displayed in templates via Bootstrap alerts:
```html
<div class="alert alert-danger">
  Book not found
</div>
```

---

## Rate Limiting (Future Enhancement)

Currently unlimited, but recommend adding:
```python
@app.route('/login')
@limiter.limit("5 per minute")
def login():
    pass
```

---

## CORS Configuration

Enabled for:
- Localhost (development)
- All origins in production (can be restricted)

Headers allowed:
- Content-Type
- Authorization

---

## Pagination

Default: 20 items per page

Example response:
```json
{
  "items": [...],
  "page": 1,
  "per_page": 20,
  "total": 100,
  "pages": 5
}
```

---

## Date/Time Format

All timestamps in ISO 8601 format: `YYYY-MM-DDTHH:MM:SS`

Example: `2024-01-15T14:30:00`

---

## Testing the API

### Using cURL
```bash
# Login
curl -X POST http://localhost:5000/login \
  -d "username=user&password=pass"

# Get books
curl http://localhost:5000/books?genre=Fiction

# Get book status
curl http://localhost:5000/api/book/1/status
```

### Using Python requests
```python
import requests

session = requests.Session()

# Login
session.post('http://localhost:5000/login', 
             data={'username': 'user', 'password': 'pass'})

# Get borrowings
resp = session.get('http://localhost:5000/api/user/borrowings')
print(resp.json())
```

---

## Changelog

### Version 2.0
- Added WebSocket real-time events
- Added REST API endpoints
- Implemented comprehensive notification system
- Added role-based API access control

### Version 1.0
- Initial release with basic CRUD operations
