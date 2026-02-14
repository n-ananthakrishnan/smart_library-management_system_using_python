# Contributing to Smart Library Management System

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to the project.

## 🎯 Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on the code, not the person
- Help others learn and grow
- Report issues responsibly

## 🚀 Getting Started

### Fork and Clone
```bash
# 1. Fork the repository on GitHub
# 2. Clone your fork
git clone https://github.com/YOUR_USERNAME/smart-library-management.git
cd smart-library-management

# 3. Add upstream remote
git remote add upstream https://github.com/ORIGINAL_OWNER/smart-library-management.git
```

### Setup Development Environment
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies with dev tools
pip install -r requirements.txt
pip install pytest pytest-cov black flake8 mypy

# Setup pre-commit hooks
pip install pre-commit
pre-commit install
```

### Create Feature Branch
```bash
# Update from main
git fetch upstream
git checkout upstream/main

# Create feature branch
git checkout -b feature/your-feature-name
```

## 📋 Development Guidelines

### Code Style

**Python**
- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Use `black` for formatting: `black app.py models.py`
- Check with `flake8`: `flake8 *.py`
- Use type hints where applicable

**HTML/Jinja2**
- Use 4-space indentation
- Keep templates semantic
- Use Bootstrap 5 classes
- Comment complex logic

**CSS**
- Use CSS custom properties for colors/sizing
- Follow BEM naming convention for classes
- Maintain dark mode compatibility
- Test responsive design (320px, 768px, 1024px)

**JavaScript**
- Use ES6+ syntax
- Comment complex logic
- Avoid global variables (use namespaces)
- Validate user input before sending

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `chore`
**Scopes**: `auth`, `books`, `borrowing`, `ui`, `db`, `api`, `realtime`

**Examples**:
```
feat(borrowing): add automatic fine calculation
fix(auth): prevent SQL injection in login query
docs(readme): update installation instructions
style(css): format stylesheet with black
refactor(models): optimize database queries
perf(api): implement query caching
test(borrowing): add unit tests for fine calculation
chore(deps): update flask-socketio to 5.3.5
```

## 🧪 Testing

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_models.py

# Run specific test
pytest tests/test_models.py::test_user_creation
```

### Writing Tests
```python
# tests/test_borrowing.py
import pytest
from app import app, db
from models import User, Book, Borrowing

@pytest.fixture
def client():
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()

def test_borrow_book(client):
    # Setup
    user = User(username='test', email='test@test.com', password_hash='hash')
    book = Book(title='Test', author='Author', isbn='123')
    db.session.add(user)
    db.session.add(book)
    db.session.commit()
    
    # Test
    borrowing = Borrowing(user_id=user.id, book_id=book.id)
    db.session.add(borrowing)
    db.session.commit()
    
    # Assert
    assert borrowing.id is not None
    assert borrowing.returned_at is None
```

## 📝 Feature Requests & Bug Reports

### Before Creating an Issue
1. Check existing issues (open and closed)
2. Search with relevant keywords
3. Read the documentation

### Creating an Issue

**Bug Report Template**:
```markdown
## Description
[Clear description of the bug]

## Steps to Reproduce
1. [First step]
2. [Second step]
3. [...]

## Expected Behavior
[What should happen]

## Actual Behavior
[What actually happens]

## Environment
- OS: [Windows/Mac/Linux]
- Python: [version]
- Browser: [name and version]

## Error Message
[Include full stack trace if applicable]

## Additional Context
[Screenshots, logs, etc.]
```

**Feature Request Template**:
```markdown
## Description
[Clear description of desired feature]

## Use Case
[Why is this feature needed?]

## Proposed Solution
[How should it work?]

## Alternative Solutions
[Other approaches considered]

## Additional Context
[Mockups, examples, etc.]
```

## 🔄 Pull Request Process

### Before Submitting

1. **Update from upstream**
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Test thoroughly**
   ```bash
   # Run all tests
   pytest

   # Check code style
   black . --check
   flake8 .

   # Run the app
   python app.py
   ```

3. **Update documentation**
   - Update README.md if needed
   - Add docstrings to new functions
   - Update CHANGELOG if applicable

### Creating PR

1. Push to your fork
   ```bash
   git push origin feature/your-feature-name
   ```

2. Create Pull Request on GitHub with:
   - Clear title: `feat(scope): description`
   - Detailed description
   - Reference to related issues: `Closes #123`
   - Checklist:
     ```
     - [ ] Tests added/updated
     - [ ] Documentation updated
     - [ ] Code follows style guidelines
     - [ ] No breaking changes
     ```

### Review Process

- At least one approval required
- CI/CD checks must pass
- All conversations must be resolved
- Finally, maintainer merges the PR

## 🏗️ Architecture Guidelines

### Adding New Features

**Authentication Feature Example**:
```python
# 1. Update models.py
class User(db.Model):
    two_factor_enabled = db.Column(db.Boolean, default=False)
    
    def enable_2fa(self):
        # Implementation
        pass

# 2. Add route in app.py
@app.route('/settings/2fa', methods=['GET', 'POST'])
@login_required
def setup_2fa():
    # Implementation
    pass

# 3. Create template templates/2fa_setup.html
# 4. Add tests tests/test_2fa.py
# 5. Update README.md with new feature
```

### Modifying Database

1. Don't modify existing models - create migrations (use Flask-Migrate if available)
2. Test data integrity
3. Document breaking changes
4. Provide migration scripts if schema changes

### Adding API Endpoints

```python
from flask import jsonify

@app.route('/api/books', methods=['GET'])
@login_required
def api_get_books():
    """
    Get all books with optional filtering.
    
    Query Parameters:
    - page: Page number (default: 1)
    - per_page: Items per page (default: 20)
    - genre: Filter by genre
    
    Returns:
    {
        "books": [...],
        "total": 100,
        "page": 1,
        "per_page": 20
    }
    """
    books = Book.query.paginate()
    return jsonify({
        'books': [book.to_dict() for book in books.items],
        'total': books.total,
        'page': books.page,
        'per_page': books.per_page
    })
```

### Real-Time Features (WebSocket)

```python
# In app.py
@socketio.on('custom_event')
@login_required
def handle_custom_event(data):
    """Handle custom real-time event"""
    # Process data
    result = process_data(data)
    
    # Emit back to user
    emit('custom_response', result, room=f'user_{current_user.id}')
    
    # Or broadcast to all
    emit('broadcast_event', result, broadcast=True)
```

## 📦 Dependency Management

### Adding New Dependencies

1. **Check if already available**
   ```bash
   pip list | grep package-name
   ```

2. **Evaluate package**
   - License compatibility
   - Maintenance status
   - Security history
   - Size and performance impact

3. **Add to requirements.txt**
   ```bash
   pip install package-name
   pip freeze > requirements.txt
   ```

4. **Document in README.md**
   - What it's used for
   - Why it was chosen
   - Any setup required

5. **Commit**
   ```bash
   git add requirements.txt
   git commit -m "chore(deps): add new-package for feature-x"
   ```

### Security Updates
- Subscribe to security notifications
- Update dependencies regularly
- Test after updating
- Document any breaking changes

## 📚 Documentation

### Code Comments
```python
def calculate_fine(borrowing_id):
    """
    Calculate overdue fine for a borrowing.
    
    Fine is calculated at $0.50 per day overdue.
    Maximum fine is 50% of book value.
    
    Args:
        borrowing_id (int): ID of the borrowing record
        
    Returns:
        float: Fine amount in dollars
        
    Raises:
        ValueError: If borrowing not found
        
    Example:
        >>> fine = calculate_fine(123)
        >>> print(f"Fine: ${fine:.2f}")
    """
    # Implementation
```

### Docstring Style
Use Google-style docstrings as shown above.

### API Documentation
Update [API_DOCS.md](API_DOCS.md) for new endpoints:
```markdown
## API Endpoints

### Get Books
```http
GET /api/books?page=1&genre=Fiction
```

**Query Parameters**:
- `page` (int): Page number, default 1
- `genre` (string): Filter by genre

**Response** (200 OK):
```json
{
  "books": [...],
  "total": 100,
  "page": 1
}
```
```

## 🎓 Topics to Explore

### If You Want to Learn
- **Database Optimization**: Query optimization, indexing strategies
- **Security**: CSRF protection, XSS prevention, input validation
- **Performance**: Caching, lazy loading, database connection pooling
- **DevOps**: Docker, CI/CD, cloud deployment
- **Testing**: Unit tests, integration tests, end-to-end tests

### Interesting Areas to Contribute
- [ ] Email notifications integration
- [ ] Advanced search with Elasticsearch
- [ ] Mobile app (Flutter/React Native)
- [ ] Analytics dashboard
- [ ] Book recommendations engine
- [ ] RFID integration
- [ ] Multi-language support
- [ ] API rate limiting
- [ ] Advanced permission system
- [ ] Book cover image recognition

## 🏆 Recognition

- Contributors are recognized in CONTRIBUTORS.md
- Major contributions may be highlighted in README.md
- Monthly contributors featured in release notes

## 📞 Questions?

- [@mention maintainers](MAINTAINERS.md) in issues
- Join our [Discord community](DISCORD_INVITE) if available
- Check existing discussions and Q&A

---

**Thank you for contributing to Smart Library Management System! 🎉**
