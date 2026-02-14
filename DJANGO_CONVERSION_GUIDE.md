"""
Django Conversion Guide
=======================

This project has been converted from Flask to Django.

## Key Changes

### 1. Project Structure
- Flask: Single app.py file, models.py
- Django: smart_library/ (project folder) + library/ (app folder)

### 2. Architecture

#### Flask -> Django Mappings:
- Flask app.config -> Django settings.py
- Flask routes (@app.route) -> Django views (views.py) + URLs (urls.py)
- Flask models (SQLAlchemy) -> Django models (models.py)
- Flask-Login -> Django auth
- Flask-SocketIO -> Django Channels

### 3. Installation & Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Run setup (creates sample data)
python manage.py init_db

# Or use the setup script
python setup_django.py
```

### 4. Running the Application

#### Standard Django:
```bash
python manage.py runserver
```

#### With WebSocket support:
```bash
daphne -b 0.0.0.0 -p 8000 smart_library.asgi:application
```

### 5. Models Changes

The SQLAlchemy models have been converted to Django models with:
- Proper field types (CharField, TextField, etc.)
- Django ORM relationships (ForeignKey, cascade delete)
- Methods preserved (is_available(), is_overdue(), etc.)
- Database indexes for performance
- Validators for data integrity

### 6. Views & Forms

- Flask views are now Django class/function-based views
- Added Django Forms for validation
- Decorators converted to Django's @login_required, custom @librarian_required
- Request/response handling is Django-native

### 7. URLs

Flask routing pattern:
```python
@app.route('/register', methods=['GET', 'POST'])
def register():
    ...
```

Django routing pattern:
```python
path('register/', views.register, name='register'),
```

### 8. Templates

Templates remain mostly the same since they're already Jinja2-compatible:
- Minor updates: url() -> {% url %}, url_for() -> {% url %}
- Request object available in context
- CSRF token handling automatic in forms

### 9. Authentication

- Flask-Login -> Django's built-in auth
- Custom User model extended from AbstractUser
- UserRole choices instead of enum
- Permission system integrated

### 10. WebSocket/Real-time

- Flask-SocketIO -> Django Channels
- New consumers.py for WebSocket handling
- AsyncWebsocketConsumer for real-time connections
- Group-based messaging for notifications

### 11. Admin Interface

- New admin.py with Django admin customization
- Automatic registration of models
- Custom list displays and filters
- Accessible at /admin/

### 12. Testing

- Django test framework (TestCase)
- Tests located in tests.py
- Run tests: python manage.py test

### 13. Environment Variables

The project uses python-dotenv. Create a .env file:

```
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
```

### 14. Database

- Default: SQLite (db.sqlite3)
- Supported: PostgreSQL, MySQL via DATABASE_URL
- Migrations: Automatic with Django
- Management: Admin interface or Django ORM

### 15. API Endpoints

RESTful endpoints for real-time data:
- /api/book/<id>/status/ - Book status
- /api/user/borrowings/ - User borrowings
- /api/stats/ - Library stats

### 16. Signals

Django signals for business logic:
- Automatic status updates on borrowing
- Notification creation on key events
- Located in library/signals/handlers.py

## File Structure

```
smart_library-management_system/
├── smart_library/           # Project configuration
│   ├── __init__.py
│   ├── settings.py         # Django settings
│   ├── urls.py             # Main URLs
│   ├── asgi.py             # Channels ASGI
│   └── wsgi.py             # WSGI
├── library/                # Main app
│   ├── models.py           # Django models
│   ├── views.py            # Views
│   ├── urls.py             # App URLs
│   ├── forms.py            # Forms
│   ├── admin.py            # Admin config
│   ├── consumers.py        # WebSocket consumers
│   ├── routing.py          # WebSocket routing
│   ├── context_processors.py
│   ├── utils.py            # Helper functions
│   ├── signals/
│   │   ├── handlers.py     # Signal handlers
│   │   └── __init__.py
│   ├── management/
│   │   └── commands/
│   │       ├── init_db.py  # Sample data command
│   │       └── setup_permissions.py
│   ├── migrations/         # Django migrations
│   └── tests.py           # Tests
├── templates/              # HTML templates (same structure)
├── static/                 # CSS, JS, images
├── manage.py              # Django CLI
├── setup_django.py        # Setup script
├── requirements.txt       # Dependencies
└── .env                   # Environment variables
```

## Migration from Flask

If you have customizations in the Flask app:

1. **Routes**: Convert to views.py and urls.py
2. **Models**: Already handled, check models.py
3. **Templates**: Copy to templates/ (mostly compatible)
4. **Static files**: Copy to static/
5. **Logic**: Add to utils.py or signals.py
6. **Decorators**: Convert to Django decorators/middleware

## Common Issues

**Issue**: "No module named 'library'"
**Solution**: Ensure INSTALLED_APPS includes 'library' in settings.py

**Issue**: "OperationalError: no such table"
**Solution**: Run `python manage.py migrate`

**Issue**: WebSocket not connecting
**Solution**: Use daphne instead of runserver, check CHANNEL_LAYERS config

**Issue**: Static files not loading
**Solution**: Run `python manage.py collectstatic --noinput`

## Next Steps

1. Customize email notifications (configure EMAIL_BACKEND)
2. Set up Celery for async tasks
3. Configure Redis for CHANNEL_LAYERS
4. Add DRF serializers for API if needed
5. Deploy using Gunicorn + Daphne + Nginx

## Documentation

- Django Docs: https://docs.djangoproject.com/
- Django Channels: https://channels.readthedocs.io/
- Django Rest Framework: https://www.django-rest-framework.org/

## Support

For issues or questions, refer to:
- Django documentation
- Django Channels documentation
- Project README.md
"""
