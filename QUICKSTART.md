# Django Setup - Quick Start

## ⚡ Installation (Windows)
```bash
setup.bat
```

## ⚡ Installation (Linux/Mac)
```bash
chmod +x setup.sh
./setup.sh
```

## ⚡ Manual Setup
```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate.bat

# Activate (Linux/Mac)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create sample data
python manage.py init_db

# Collect static files
python manage.py collectstatic --noinput
```

## 🚀 Running the Application

### Option 1: Standard Django
```bash
python manage.py runserver
```
Access at: http://localhost:8000/

### Option 2: With WebSocket Support
```bash
daphne -b 0.0.0.0 -p 8000 smart_library.asgi:application
```
Access at: http://localhost:8000/

## 🔑 Default Credentials
- **Username:** admin
- **Password:** admin123
- **Admin URL:** http://localhost:8000/admin/

## 📝 Important: Update Templates

The templates need minor updates to work with Django:
1. Replace `url_for()` with `{% url %}`
2. Replace `current_user` with `request.user`
3. Add `{% load static %}` tag
4. Update form rendering

See **TEMPLATE_CONVERSION_NOTES.md** for detailed instructions.

## 📚 Documentation

- **DJANGO_CONVERSION_GUIDE.md** - Complete conversion guide
- **TEMPLATE_CONVERSION_NOTES.md** - Template update instructions
- **CONVERSION_COMPLETE.md** - Full summary of changes

## ✅ What Works

✓ User Authentication
✓ Book Management
✓ Borrowing System
✓ Reservations
✓ Reviews & Ratings
✓ Barcode Scanning
✓ QR Code Generation
✓ Activity Logging
✓ Real-time Notifications
✓ Admin Interface

## ⚙️ Environment Variables

Create a `.env` file:
```
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
```

## 🧪 Running Tests

```bash
python manage.py test
```

## 🐛 Troubleshooting

**Error: "No module named 'library'"**
- Ensure you're in the correct project directory

**Error: "OperationalError: no such table"**
- Run: `python manage.py migrate`

**WebSocket not working**
- Use daphne instead of runserver
- Install redis: `pip install redis`

**Static files missing**
- Run: `python manage.py collectstatic --noinput`

## 📞 Need Help?

Refer to:
1. DJANGO_CONVERSION_GUIDE.md
2. Django documentation: https://docs.djangoproject.com/
3. Django Channels: https://channels.readthedocs.io/
4. Template notes: TEMPLATE_CONVERSION_NOTES.md
