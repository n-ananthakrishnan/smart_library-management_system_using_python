# Smart Library Management System <img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python 3.8+"> <img src="https://img.shields.io/badge/Flask-3.0.0-green.svg" alt="Flask">

A modern, innovative library management system built with Flask, featuring real-time notifications, barcode scanning, QR code generation, and a comprehensive borrowing workflow. Designed for educational institutions to streamline book management and member interactions.

## ✨ Key Features

### Core Functionality
- 📚 **Book Management** - Add, edit, delete, and categorize books with comprehensive metadata
- 👥 **User Authentication** - Secure registration and login with role-based access control
- 🔐 **Role-Based Access** - Student and Librarian roles with different permission levels
- 📖 **Borrowing System** - Complete borrowing workflow with due dates and overdue tracking
- 💾 **Reservations** - Students can reserve books when unavailable
- ⭐ **Review & Rating** - 5-star rating system with user reviews

### Real-Time Features
- 🔔 **Real-Time Notifications** - Instant WebSocket-based alerts for book availability, reminders, and overdue notices
- 📊 **Live Dashboard** - Real-time statistics and activity streaming
- 🔄 **Instant Updates** - Cross-browser synchronization of book status and borrowing data

### Advanced Features
- 📱 **Barcode Scanning** - Scan books via webcam using OpenCV and pyzbar
- 📲 **QR Code Generation** - Generate shareable QR codes for book identification
- 📈 **Activity Logging** - Comprehensive tracking of all library operations for analytics
- 💰 **Fine Management** - Automatic calculation of overdue fines
- 🌙 **Dark Mode** - Responsive dark theme support with localStorage preference saving
- 📱 **Responsive Design** - Mobile-first design using Bootstrap 5

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Modern web browser (Chrome, Firefox, Safari, Edge)
- Webcam (optional, for barcode scanning features)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/smart-library-management.git
   cd smart-library-management
   ```

2. **Create a virtual environment**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   # Copy the example .env file
   cp .env .env.local  # macOS/Linux
   # or
   copy .env .env.local  # Windows

   # Edit .env.local and update:
   # - SECRET_KEY: Generate with: python -c "import secrets; print(secrets.token_hex(32))"
   # - DATABASE_URL if using different database
   ```

5. **Initialize the database**
   ```bash
   python
   >>> from app import app, db
   >>> with app.app_context():
   ...     db.create_all()
   >>> exit()
   ```

6. **Create a test librarian account** (optional)
   ```bash
   python
   >>> from app import app, db
   >>> from models import User, UserRole
   >>> from werkzeug.security import generate_password_hash
   >>> 
   >>> with app.app_context():
   ...     user = User(
   ...         username='librarian',
   ...         email='librarian@library.com',
   ...         full_name='Head Librarian',
   ...         password_hash=generate_password_hash('password123'),
   ...         role=UserRole.LIBRARIAN
   ...     )
   ...     db.session.add(user)
   ...     db.session.commit()
   >>> exit()
   ```

7. **Run the application**
   ```bash
   python app.py
   ```

   The application will be available at: `http://localhost:5000`

## 📖 Usage

### Default Accounts

**Librarian Account** (if created):
- Username: `librarian`
- Password: `password123`
- Role: Full access to all features, book management, and analytics

### Student Registration
1. Click "Register" on the login page
2. Fill in your details (Full Name, Email, Username, Password, Roll Number)
3. Click "Create Account"
4. Login with your credentials

### Basic Workflows

**Browsing Books**
1. After login, click "Browse Books" from dashboard
2. Use search bar to find specific books
3. Filter by genre using the dropdown
4. Click "View Details" to see book information, reviews, and borrowing options

**Borrowing a Book**
1. Navigate to book details page
2. If book is available, click "Borrow Book"
3. Confirm the borrowing
4. Due date will be set to 14 days from borrowing date

**Returning a Book**
1. Go to "My Dashboard"
2. Find the book in "Active Borrowings" section
3. Click "Return Book" button
4. Confirm the return

**Scanning Books** (Librarian only)
1. Click "Scan Books" from dashboard
2. Enter the rack number where books should be physically Located
3. Click "Start Scanning"
4. Point webcam at barcode on book spine
5. System will verify if book is in correct location

## 📊 Project Structure

```
smart-library-management/
├── app.py                          # Main Flask application (620 lines)
├── models.py                       # Database models and schema (280 lines)
├── requirements.txt                # Python dependencies
├── .env                           # Environment configuration (copy to .env.local)
├── .gitignore                     # Git ignore rules
├── README.md                      # This file
├── instance/                      # Flask instance folder (database files)
├── static/
│   ├── css/
│   │   └── style.css             # Modern CSS system with dark mode
│   ├── js/
│   │   └── main.js               # Socket.IO client and utilities
│   └── uploads/                  # User-uploaded files
└── templates/
    ├── base.html                 # Master template
    ├── login.html                # Authentication page
    ├── register.html             # User registration
    ├── index.html                # Landing page
    ├── student_dashboard.html    # Student view
    ├── librarian_dashboard.html  # Librarian analytics view
    ├── list_books.html           # Book catalog
    ├── book_detail.html          # Book details and reviews
    ├── add_book.html             # Create new book (librarian)
    ├── edit_book.html            # Modify existing book (librarian)
    ├── scan.html                 # Barcode scanning interface
    ├── scan_result.html          # Scan result display
    ├── notifications.html        # User notification history
    ├── 404.html                  # Page not found error
    └── 500.html                  # Server error page
```

## 🏗️ Architecture

### Database Schema

**User Model**
- Multi-role system: STUDENT, LIBRARIAN, ADMIN
- Secure password hashing with Werkzeug
- Email and username uniqueness constraints
- Relationship tracking to borrowings and reviews

**Book Model**
- Comprehensive metadata: ISBN, author, publisher, genre, edition, pages
- Availability tracking and copy management
- Average rating calculation from reviews
- Barcode and QR code generation support

**Borrowing Model**
- Complete loan lifecycle tracking
- Due date management with overdue detection
- Automatic fine calculation (customizable rate)
- Return timestamp recording

**Additional Models**
- **Reservation**: Future book holds when unavailable
- **Review**: 5-star ratings with reviewer reference
- **ActivityLog**: Comprehensive audit trail (12 action types)
- **Notification**: Real-time alert system with expiration

### Technology Stack

**Backend**
- **Flask 3.0.0** - Web framework
- **Flask-SQLAlchemy 3.1.1** - ORM for database interactions
- **Flask-Login 0.6.3** - User session management
- **Flask-SocketIO 5.3.5** - Real-time WebSocket communication
- **SQLite** - Lightweight database (production: PostgreSQL recommended)

**Frontend**
- **Bootstrap 5.3.0** - Responsive CSS framework
- **Socket.IO 4.5.4** - Real-time client communication
- **Font Awesome 6.4.0** - Icon library
- **Poppins** - Typography via Google Fonts

**Advanced Features**
- **OpenCV 4.8.1.78** - Camera and image processing
- **pyzbar 0.1.9** - Barcode decoding
- **qrcode 7.4.2** - QR code generation
- **Pillow 10.1.0** - Image processing
- **python-dotenv** - Environment configuration

## 🔐 Security Features

- Password hashing using Werkzeug security
- CSRF protection via Flask Session
- SQL injection prevention via SQLAlchemy ORM
- Role-based access control decorators
- Secure cookie-based sessions
- Input validation on all forms
- File upload restrictions (16MB limit, whitelisted extensions)

## ⚙️ Configuration

### Environment Variables (.env)

```env
# Flask
FLASK_APP=app.py
FLASK_ENV=development
DEBUG=True

# Database
DATABASE_URL=sqlite:///library.db

# Security
SECRET_KEY=your-random-secret-key-here

# Application
MAX_CONTENT_LENGTH=16777216
ENABLE_BARCODE_SCANNING=True
ENABLE_QR_CODE=True
```

### Customizable Settings

In `models.py`, you can adjust:
- **FINE_RATE**: Overdue fine amount per day
- **BORROW_DURATION**: Default borrowing period (days)
- **RESERVATION_DURATION**: Reservation hold period (days)

## 🚀 Deployment

### Development
```bash
python app.py
# Runs on http://localhost:5000 with auto-reload
```

### Production

1. **Update `.env` for production**
   ```env
   FLASK_ENV=production
   DEBUG=False
   SECRET_KEY=generate-new-random-key-16-char-minimum
   ```

2. **Use production database** (PostgreSQL recommended)
   ```env
   DATABASE_URL=postgresql://user:password@localhost/librarydb
   ```

3. **Deploy using WSGI server** (Gunicorn recommended)
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

4. **Setup reverse proxy** (Nginx/Apache recommended)
   - Configure SSL/TLS certificates
   - Enable gzip compression
   - Setup static file serving

## 📱 API Endpoints

### Public Routes
- `GET /` - Landing page
- `GET /login` - Login page
- `POST /login` - Process login
- `GET /register` - Registration page
- `POST /register` - Create account

### Protected Routes
- `GET /dashboard` - User dashboard
- `GET /books` - Book catalog
- `GET /book/<id>` - Book details
- `GET /notifications` - Notification history

### Librarian Routes
- `GET /add-book` - Add book form
- `POST /add-book` - Create book
- `GET /edit-book/<id>` - Edit form
- `POST /edit-book/<id>` - Update book
- `POST /delete-book/<id>` - Delete book
- `GET /scan` - Barcode scanner
- `GET /librarian-dashboard` - Analytics view

### API Endpoints (JSON)
- `GET /api/book/<id>/status` - Book availability status
- `GET /api/user/borrowings` - User's active borrowings
- `GET /api/stats` - Library statistics

### WebSocket Events
- `connect` - Initialize real-time connection
- `notification` - Receive alerts
- `updates` - Dashboard data updates

## 📊 Features in Detail

### Real-Time Notifications
- Automatic notifications for:
  - Book becoming available (if reserved)
  - Approaching due dates
  - Overdue books
  - Borrowing confirmations
  - System announcements

### Dashboard Analytics (Librarian)
- Total books and availability status
- Member statistics
- Borrow/return activity log
- Overdue tracking
- Fine calculation and tracking

### Search & Filter
- Full-text search across book titles and authors
- Genre-based filtering
- Availability status filtering
- Sort by title, author, or rating

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Troubleshooting

### Database Errors
```bash
# Reset database
rm instance/smart_library.db
python app.py  # Will recreate on startup
```

### Dependencies Issues
```bash
pip install --upgrade -r requirements.txt
```

### Barcode Scanning Not Working
- Ensure webcam permissions are granted
- Check that OpenCV and pyzbar are properly installed
- Try with different barcode angles and distances

### Real-Time Features Not Working
- Clear browser cache (Ctrl+Shift+Delete)
- Check browser console for WebSocket errors
- Verify Socket.IO is loaded from CDN

## 📞 Support & Contact

For issues, questions, or feature requests:
- Open an issue on GitHub
- Check existing documentation
- Review troubleshooting section

## 🎓 Educational Use

This system is designed for educational institutions. Features can be customized for:
- School libraries
- College/University libraries
- Corporate libraries
- Public library systems

---

**Last Updated**: 2024
**Version**: 2.0 (Modern Redesign with Real-Time Features)
