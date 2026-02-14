# Quick Reference Guide

Fast lookup for common tasks and troubleshooting.

## 🚀 Quick Start

### Windows
```bash
setup.bat
python app.py
```

### macOS/Linux
```bash
chmod +x setup.sh
./setup.sh
python app.py
```

Then open: `http://localhost:5000`

---

## 📋 Common Tasks

### Create Admin User
```python
python
>>> from app import app, db
>>> from models import User, UserRole
>>> from werkzeug.security import generate_password_hash
>>> 
>>> with app.app_context():
...     user = User(
...         username='admin',
...         email='admin@library.com',
...         full_name='Administrator',
...         password_hash=generate_password_hash('admin123'),
...         role=UserRole.LIBRARIAN  # Or create separate ADMIN role
...     )
...     db.session.add(user)
...     db.session.commit()
...     print(f"Admin created with ID: {user.id}")
```

### Reset Database
```bash
# Delete the database file
rm instance/smart_library.db

# Restart app (recreates on startup)
python app.py
```

### Add Sample Books
```python
python
>>> from app import app, db
>>> from models import Book
>>>
>>> with app.app_context():
...     books = [
...         Book(title='Python Programming', author='John Doe', 
...              isbn='123-456', barcode='111111', genre='Programming'),
...         Book(title='Clean Code', author='Robert Martin',
...              isbn='234-567', barcode='222222', genre='Programming')
...     ]
...     db.session.add_all(books)
...     db.session.commit()
...     print("Sample books added")
```

### Check Overdue Books
```python
python
>>> from app import app
>>> from models import Borrowing
>>> from datetime import datetime
>>>
>>> with app.app_context():
...     overdue = Borrowing.query.filter(
...         Borrowing.due_date < datetime.utcnow(),
...         Borrowing.returned_at == None
...     ).all()
...     print(f"Overdue books: {len(overdue)}")
...     for b in overdue:
...         days = (datetime.utcnow() - b.due_date).days
...         fine = days * 0.50
...         print(f"  {b.book.title}: {days} days overdue, Fine: ${fine:.2f}")
```

### View All Users
```python
python
>>> from app import app
>>> from models import User
>>>
>>> with app.app_context():
...     users = User.query.all()
...     for user in users:
...         print(f"{user.id}: {user.full_name} ({user.username}) - {user.role}")
```

### Export Borrowing History
```python
python
>>> from app import app
>>> from models import ActivityLog
>>> import csv
>>>
>>> with app.app_context():
...     activities = ActivityLog.query.filter_by(action='borrow').all()
...     with open('borrowing_history.csv', 'w') as f:
...         writer = csv.writer(f)
...         writer.writerow(['Date', 'User', 'Book', 'Action'])
...         for activity in activities:
...             writer.writerow([
...                 activity.timestamp,
...                 activity.user.full_name,
...                 activity.book.title if activity.book else 'N/A',
...                 activity.action
...             ])
...     print("Export complete")
```

---

## 🔧 Configuration

### Essential Settings (.env)
```env
# Required
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secure-random-key
DATABASE_URL=sqlite:///library.db

# Optional
DEBUG=True
ENABLE_BARCODE_SCANNING=True
MAX_CONTENT_LENGTH=16777216
```

### Customize Borrowing Rules
Edit in `models.py`:
```python
# Borrowing class constants
FINE_RATE = 0.50  # $ per day
BORROW_DURATION = 14  # days
```

### Database Persistence
- Development: SQLite (automatic)
- Production: PostgreSQL recommended
  ```env
  DATABASE_URL=postgresql://user:password@localhost/library
  ```

---

## 🆘 Troubleshooting

### Port Already in Use
```bash
# Windows - Find process using port 5000
netstat -ano | findstr :5000

# Kill the process
taskkill /PID <PID> /F

# Or use different port
python app.py --port 5001
```

### Database Locked
```bash
# Close any open connections
# Delete lock file if exists
rm instance/smart_library.db-journal

# Restart app
python app.py
```

### Module Not Found
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate.bat  # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

### WebSocket Connection Failed
```
Check:
1. Firewall allows WebSocket (port 5000+)
2. Browser console for errors
3. Socket.IO library loaded
4. Not behind corporate proxy
```

### Barcode Scanning Not Working
```bash
# Check OpenCV installation
python -c "import cv2; print(cv2.__version__)"

# Check camera access
# Windows: Settings > Privacy > Camera
# macOS: System Preferences > Security & Privacy > Camera
# Linux: Check permissions - sudo usermod -a -G video $USER
```

### Slow Database Queries
```python
# Enable query logging
app.config['SQLALCHEMY_ECHO'] = True

# Check indexes
>>> from app import db
>>> db.engine.table_names()

# Analyze slow queries with:
SELECT * FROM sqlite_stat1;
```

---

## 📊 Monitoring

### Check Application Health
```bash
curl http://localhost:5000/health
# Response: {"status": "healthy", "version": "2.0"}
```

### View User Sessions
```python
python
>>> from flask import session
>>> # Sessions stored in secure cookies (not visible without secret key)
```

### Monitor Database Size
```bash
# Check database file size
ls -lh instance/smart_library.db

# Database stats
sqlite3 instance/smart_library.db "SELECT name, count(*) as rows FROM sqlite_master WHERE type='table' GROUP BY name;"
```

---

## 🔐 Security Checklist

- [ ] Changed `SECRET_KEY` from default
- [ ] Set `DEBUG=False` in production
- [ ] HTTPS enabled (SSL certificate)
- [ ] Strong database password set
- [ ] Regular database backups
- [ ] User input validation active
- [ ] CORS properly configured
- [ ] File upload size limited
- [ ] Admin accounts secured
- [ ] Dependencies up to date

---

## 📱 Testing Routes

### Manual Testing Checklist

**Authentication**
- [ ] Register new account
- [ ] Login with credentials
- [ ] Logout clears session
- [ ] Password reset works
- [ ] Remember login works

**Books**
- [ ] View book catalog
- [ ] Search by title/author
- [ ] Filter by genre
- [ ] View book details
- [ ] View QR code

**Borrowing**
- [ ] Borrow available book
- [ ] Cannot borrow unavailable
- [ ] Return book reduces fine
- [ ] Reserve unavailable book
- [ ] Notification on availability

**Reviews**
- [ ] Add review to borrowed book
- [ ] Rating updates average
- [ ] Cannot review unborowed book
- [ ] Edit existing review

**Admin**
- [ ] Add new book
- [ ] Edit book details
- [ ] Delete book (soft delete)
- [ ] Scan barcode
- [ ] View statistics

---

## 🔄 Deployment Checklist

### Pre-Deployment
- [ ] All tests passing
- [ ] No console errors
- [ ] Database optimized
- [ ] Environment variables set
- [ ] Static files collected
- [ ] SSL certificate obtained

### Post-Deployment
- [ ] Health check passes
- [ ] Logins work
- [ ] Real-time updates functional
- [ ] Email notifications working
- [ ] Backups configured
- [ ] Monitoring enabled
- [ ] Error logging active

---

## 📚 Useful Commands

### Development
```bash
# Activate environment
source venv/bin/activate

# Run app with auto-reload
python app.py

# Run with debugger
FLASK_ENV=development FLASK_DEBUG=1 python app.py

# Run tests
pytest

# Check code style
black . --check
flake8 .
```

### Database
```bash
# Interactive shell
python
>>> from app import app, db

# View database schema
sqlite3 instance/smart_library.db ".schema"

# Backup database
cp instance/smart_library.db instance/smart_library_backup.db

# Reset database
rm instance/smart_library.db
```

### Virtual Environment
```bash
# Create
python -m venv venv

# Activate (Linux/macOS)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate.bat

# Deactivate
deactivate

# Delete
rm -rf venv
```

---

## 🌐 URL Reference

| Page | URL | Requires Auth | Requires Role |
|------|-----|---------------|---------------|
| Landing | `/` | No | - |
| Login | `/login` | No | - |
| Register | `/register` | No | - |
| Dashboard | `/dashboard` | Yes | Student |
| Books | `/books` | Yes | Student |
| Book Details | `/book/<id>` | Yes | Student |
| Add Book | `/add-book` | Yes | Librarian |
| Edit Book | `/edit-book/<id>` | Yes | Librarian |
| Scan | `/scan` | Yes | Librarian |
| Notifications | `/notifications` | Yes | Student |
| Librarian Dashboard | `/librarian-dashboard` | Yes | Librarian |

---

## 💾 File Locations

| File | Purpose | Location |
|------|---------|----------|
| Database | SQLite DB | `instance/smart_library.db` |
| Uploads | User Files | `static/uploads/` |
| Styles | CSS | `static/css/style.css` |
| Scripts | JavaScript | `static/js/main.js` |
| Templates | HTML | `templates/` |
| Config | .env file | `.env.local` |
| Models | ORM Classes | `models.py` |
| Routes | Flask Routes | `app.py` |

---

## 🎯 Performance Tips

### Frontend
- Enable gzip compression
- Minify CSS/JavaScript
- Cache static assets (30 days)
- Lazy load images
- Use CDN for libraries

### Backend
- Enable query caching
- Use database connection pooling
- Optimize SQL queries
- Implement pagination
- Use async for I/O

### Database
- Create indexes on frequently queried columns
- Archive old activity logs
- Vacuum database periodically
- Monitor slow queries

---

## 📞 Support Resources

- **Documentation**: See README.md
- **API Reference**: See API_DOCS.md
- **Deployment Help**: See DEPLOYMENT.md
- **Contributing**: See CONTRIBUTING.md
- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions

---

## 📝 Notes

Keep this handy for:
- Quick problem solving
- Common operations
- Configuration reference
- Testing checklist
- Deployment guide

Last Updated: January 2024
Version: 2.0
