# Smart Library Management System - Functions & Features

## 📋 Complete Feature List

### 🔐 **Authentication & User Management**

| Feature | Description | Route | Role |
|---------|-------------|-------|------|
| **Registration** | New user sign up with email, username, password | `/register` | Public |
| **Login** | User authentication with session management | `/login` | Public |
| **Logout** | Clear user session and sign out | `/logout` | Authenticated |
| **Profile Management** | View and manage user profile (built-in) | - | Authenticated |
| **Role-Based Access** | Three roles: Student, Librarian, Admin | - | System-wide |

**Key Features**:
- ✅ Email and username uniqueness validation
- ✅ Password hashing with Werkzeug security
- ✅ Remember login functionality
- ✅ Automatic role assignment (defaults to Student)
- ✅ User deactivation support

---

### 📚 **Book Management**

#### View & Browse
| Feature | Description | Route | Access |
|---------|-------------|-------|--------|
| **View All Books** | Browse library catalog with pagination | `/books` | Authenticated |
| **Search Books** | Search by title, author, or ISBN | `/books?q=query` | Authenticated |
| **Filter by Genre** | Filter books by genre category | `/books?genre=Fiction` | Authenticated |
| **Filter by Status** | View available/borrowed/reserved books | `/books?status=available` | Librarian+ |
| **View Book Details** | Full book information and reviews | `/book/<id>` | Authenticated |
| **View Ratings** | See average rating and reviews | `/book/<id>` | Authenticated |

#### Book Administration (Librarian Only)
| Feature | Description | Route |
|---------|-------------|-------|
| **Add Book** | Add new book to library | `/add_book` |
| **Edit Book** | Modify book information | `/edit/<id>` |
| **Delete Book** | Remove book from library | `/delete/<id>` |
| **Update Availability** | Change copy count and status | Auto-updated |

**Book Details Stored**:
- Title, Author, ISBN, Barcode
- Genre, Category, Edition
- Publisher, Publication Year, Pages
- Total & Available Copies
- Rack & Shelf Location
- Description
- Cover Image (placeholder/upload)
- Status (Available/Borrowed/Reserved/Lost/Maintenance)
- Average Rating

---

### 📖 **Borrowing System**

| Feature | Description | Route | Details |
|---------|-------------|-------|---------|
| **Borrow Book** | Check out available book | `/borrow/<id>` | 14-day loan period |
| **Return Book** | Return borrowed book | `/return/<id>` | Auto-calculates fine |
| **View Active Borrowings** | See currently borrowed books | Dashboard | Real-time updates |
| **Track Due Dates** | Monitor when books are due | Dashboard | Color-coded status |
| **Calculate Fines** | Auto-compute overdue penalties | On return | $0.50/day |
| **View Overdue Books** | See past-due items | Dashboard | With fine amounts |
| **Borrow Limits** | Prevent exceeding max borrowings | System | Max 5 active borrows |

**Borrowing Rules**:
- Default loan period: 14 days
- Overdue fine: $0.50 per day
- Cannot borrow same book twice
- Available copies must be > 0
- Automatic status updates

---

### 🔖 **Reservation System**

| Feature | Description | Route | Purpose |
|---------|-------------|-------|---------|
| **Reserve Book** | Hold unavailable book | `/reserve/<id>` | Wait list management |
| **View Reservations** | See pending reserves | Dashboard | Track status |
| **Auto-Notification** | Alert when book available | Real-time | WebSocket |
| **Reserve Cancellation** | Remove from wait list | System | Cleanup |
| **Hold Period** | Temporary hold duration | 7 days default | Configurable |

---

### ⭐ **Review & Rating System**

| Feature | Description | Route | Details |
|---------|-------------|-------|---------|
| **Add Review** | Submit 5-star rating + text | `/book/<id>/review` | Per user, per book |
| **Update Review** | Edit existing review | `/book/<id>/review` | Timestamped |
| **View Reviews** | See all book reviews | `/book/<id>` | Paginated list |
| **Calculate Avg Rating** | Automatic rating aggregation | System | Updates instantly |
| **Review Stats** | Total reviews per book | Dashboard | Display metric |

**Review Features**:
- ✅ 1-5 star rating system
- ✅ Optional review text
- ✅ Reviewer attribution
- ✅ Timestamp tracking
- ✅ Edit capability
- ✅ Average rating calculation

---

### 🔔 **Notification System**

| Feature | Description | Trigger | Type |
|---------|-------------|---------|------|
| **Borrow Confirmation** | Confirm successful borrow | On borrow | `borrow` |
| **Return Confirmation** | Confirm successful return | On return | `return` |
| **Overdue Reminder** | Due date approaching | 24hrs before | `reminder` |
| **Overdue Alert** | Book is now overdue | Past due date | `overdue` |
| **Availability Alert** | Reserved book available | On return | `available` |
| **System Announcement** | General library notices | Admin | `info` |
| **Reservation Confirm** | Reserve request accepted | On reserve | `reservation` |

**Delivery Methods**:
- 🔴 Real-time: WebSocket push notifications (immediate, in-app)
- 📧 Future: Email notifications (planned)
- 📱 Future: SMS alerts (planned)

**Notification Features**:
- ✅ Auto-expiration (30 days)
- ✅ Mark as read
- ✅ Filter by type
- ✅ History view
- ✅ Real-time WebSocket delivery

---

### 🔍 **Barcode Scanning**

| Feature | Description | Route | Requirements |
|---------|-------------|-------|--------------|
| **Scan Books** | Webcam barcode scanning | `/scan` | Librarian+ |
| **Real-Time Decode** | Live barcode detection | WebSocket | OpenCV + pyzbar |
| **Verify Location** | Check if in correct rack | System | Rack entered |
| **Misplaced Alert** | Notify if book in wrong location | On scan | Alert display |
| **Quick Check-in** | Fast inventory verification | On scan | Activity logged |

**Scanning Features**:
- ✅ OpenCV camera integration
- ✅ pyzbar barcode decoding
- ✅ Real-time frame processing
- ✅ Location validation
- ✅ Activity audit trail

---

### 🎫 **QR Code System**

| Feature | Description | Route | Format |
|---------|-------------|-------|--------|
| **Generate QR Code** | Create book identification QR | `/book/<id>/qr` | PNG image |
| **Display QR** | Show in book modal/printable | `/book/<id>` | Base64 encoded |
| **Share QR** | Shareable QR code link | System | Via email/print |
| **QR Scanning** | Future: Mobile app scanning | Planned | iOS/Android |

---

### 📊 **Dashboard & Analytics**

#### Student Dashboard
| Component | Shows | Updates |
|-----------|-------|---------|
| **Active Borrowings** | Currently borrowed books | Real-time |
| **Overdue Status** | Books past due with fines | Real-time |
| **Upcoming Due Dates** | Books due soon (color-coded) | Every 30 seconds |
| **Notifications** | Latest 5 alerts | Real-time WebSocket |
| **Quick Actions** | Browse, Scan, View All | Navigation |
| **Stats Cards** | Books borrowed, Overdue count, Fine due | Real-time |

#### Librarian Dashboard
| Component | Shows | Updates |
|-----------|-------|---------|
| **Library Stats** | Total books, available, borrowed | Real-time |
| **Member Stats** | Total/active members, borrowing count | Real-time |
| **Activity Timeline** | Recent library operations (10 latest) | Real-time |
| **Overdue Tracking** | Books past due with member info | Real-time |
| **Genre Breakdown** | Books by category | On-demand |
| **Quick Links** | Add book, Manage books, Scan books | Navigation |

---

### 🌐 **API Endpoints**

#### Book Status API
```
GET /api/book/<id>/status
```
Returns: Book metadata, availability, current borrower status

#### User Borrowings API
```
GET /api/user/borrowings
```
Returns: Active borrowings, overdue count, fine total, due dates

#### Statistics API
```
GET /api/stats
```
Returns: System-wide stats for analytics (Librarian only)

---

### 🔌 **WebSocket Real-Time Events**

| Event | Direction | Payload | Purpose |
|-------|-----------|---------|---------|
| **connect** | Server → Client | User ID, status | Initialize connection |
| **disconnect** | Server → Client | - | Clean up session |
| **notification** | Server → Client | Title, message, type | Push alerts |
| **updates** | Server → Client | Borrowing stats | Dashboard refresh |
| **get_updates** | Client → Server | - | Request fresh data |

**Real-Time Features**:
- ✅ Automatic user room joining
- ✅ Targeted notifications (user-specific)
- ✅ Live dashboard updates
- ✅ Message broadcasting
- ✅ Connection persistence

---

### 📝 **Activity Logging**

All major actions automatically logged with:
- User ID
- Book ID (if applicable)
- Action type (borrow, return, search, etc.)
- Timestamp
- IP address
- Additional details

**Logged Actions** (12 types):
1. `register` - New user signup
2. `login` - User login
3. `logout` - User logout
4. `search` - Book search
5. `view_book` - View details
6. `add_book` - New book added
7. `edit_book` - Book updated
8. `delete_book` - Book removed
9. `borrow` - Book borrowed
10. `return` - Book returned
11. `reserve` - Book reserved
12. `review` - Review added

**Uses**: Analytics, auditing, security tracking, usage analytics

---

## 🛠️ **Technical Functions**

### Helper Functions

| Function | Purpose | Parameters |
|----------|---------|-----------|
| `load_user()` | Flask-Login user loader | user_id |
| `librarian_required()` | Route decorator | function |
| `log_activity()` | Record user action | action, book_id, user_id, details |
| `create_notification()` | Send real-time alert | user_id, title, message, type |
| `is_overdue()` | Check if book past due | self (Borrowing object) |
| `calculate_fine()` | Compute overdue fee | self (Borrowing object) |
| `get_active_borrowings()` | Get user's current loans | self (User object) |
| `get_current_borrower()` | Get who has book | self (Book object) |

---

## 🔐 **Security Features**

- ✅ Password hashing (Werkzeug)
- ✅ SQL injection prevention (SQLAlchemy ORM)
- ✅ CSRF protection (Flask session)
- ✅ Role-based access control
- ✅ User authentication required
- ✅ Secure cookies
- ✅ Input validation (all forms)
- ✅ File upload restrictions (16MB max)
- ✅ Environment-based secrets

---

## 🚀 **Performance Features**

- ✅ Database pagination (12 items/page)
- ✅ Indexed queries
- ✅ Real-time WebSocket (vs polling)
- ✅ Caching of static assets
- ✅ Connection pooling ready
- ✅ Lazy loading of relationships

---

## 📱 **User Interfaces**

| Page | Purpose | Features |
|------|---------|----------|
| **Landing Page** | Home & overview | Hero section, stats, features |
| **Login Page** | Authentication | Credentials input, remember option |
| **Register Page** | Sign up | Full name, email, username, password |
| **Student Dashboard** | User control panel | Borrowings, notifications, stats |
| **Librarian Dashboard** | Admin view | Analytics, activity log, stats |
| **Book Catalog** | Browse books | Search, filter, pagination, grid |
| **Book Details** | Full information | Metadata, reviews, actions, QR |
| **Add/Edit Book** | Book management | Form with 13+ fields |
| **Scan Interface** | Barcode scanner | Webcam, location verification |
| **Notifications** | Alert center | History, filtering, pagination |
| **Error Pages** | Error display | 404, 500 with navigation |

---

## 📊 **Database Models**

### User
- Authentication (username, email, password_hash)
- Profile (full_name, roll_number)
- Role-based access (student/librarian/admin)
- Active status
- Relationships: borrowings, reviews, reservations, notifications, activity_logs

### Book
- Metadata (title, author, isbn, barcode, genre, etc.)
- Availability (total_copies, available_copies, status)
- Location (rack_no, shelf_no, last_location_verified)
- Rating (average_rating, calculated from reviews)
- Timestamps (added_at, updated_at)
- Relationships: borrowings, reservations, reviews, activity_logs

### Borrowing
- User reference
- Book reference
- Loan tracking (borrowed_date, due_date, returned_at)
- Fine tracking (fine_paid, is_overdue calculation)
- Status (active/completed)
- Methods: is_overdue(), calculate_fine()

### Reservation
- User reference
- Book reference
- Status (is_fulfilled)
- Timestamps (created_at, canceled_at)
- Hold period management

### Review
- User & Book reference
- Rating (1-5 stars)
- Review text
- Helpful counter
- Timestamps

### ActivityLog
- User & Book reference
- Action type (12 types)
- Details JSON
- IP address
- Complete audit trail

### Notification
- User reference
- Message (title, message)
- Type (borrow, return, reminder, etc.)
- Status (is_read)
- Expiration (expires_at)
- Timestamps

---

## 🎯 **Summary**

The Smart Library Management System provides:

✅ **21 Routes** - Complete user workflows
✅ **12+ Models** - Comprehensive data relationships  
✅ **Real-time Features** - WebSocket notifications
✅ **3 User Roles** - Tiered access control
✅ **Complete Borrowing System** - Loans, returns, fines
✅ **Advanced Features** - Reservations, reviews, scanning, QR codes
✅ **Modern UI** - Responsive, dark mode, real-time dashboards
✅ **Security** - Password hashing, role-based access, input validation
✅ **Analytics** - Activity logging, notifications, stats
✅ **API Ready** - JSON endpoints for integration

---

**Total Features**: 40+
**Total Routes**: 21
**Total Database Models**: 7
**Real-Time Capabilities**: WebSocket + REST API
**Status**: Production Ready ✨

