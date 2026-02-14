#!/bin/bash

# Smart Library Management System - Django Setup Script (macOS/Linux)
# Converts Flask to Django and initializes the project

set -e

echo "🚀 Smart Library Management System - Django Setup"
echo "=================================================="
echo ""

# Check Python version
echo "📋 Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | awk '{print $2}')
echo "✓ Python $PYTHON_VERSION found"
echo ""

# Create virtual environment
echo "🔧 Setting up virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
source venv/bin/activate
echo "✓ Virtual environment activated"
echo ""

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip setuptools wheel > /dev/null
echo "✓ pip upgraded"
echo ""

# Install dependencies
echo "📦 Installing Django dependencies..."
pip install -r requirements.txt
echo "✓ Dependencies installed"
echo ""

# Create .env file if it doesn't exist
echo "⚙️  Configuring environment..."
if [ ! -f ".env" ]; then
    echo "ℹ️  Creating .env for Django..."
    cat > .env << 'EOF'
SECRET_KEY=dev-key-change-in-production-$(date +%s)
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
EOF
    echo "✓ .env created"
else
    echo "✓ .env already exists"
fi
echo ""

# Create necessary directories
echo "📁 Creating required directories..."
mkdir -p media/profiles media/book_covers
echo "✓ Directories created"
echo ""

# Run migrations
echo "🗄️  Running Django migrations..."
python manage.py migrate
echo "✓ Migrations completed"
echo ""

# Create sample data
echo "👥 Creating sample data..."
python manage.py init_db
echo "✓ Sample data created"
echo ""

# Collect static files
echo "📦 Collecting static files..."
python manage.py collectstatic --noinput
echo "✓ Static files collected"
echo ""

echo "✨ Setup complete!"
echo ""
echo "🚀 To start the application, run:"
echo "   source venv/bin/activate"
echo "   python manage.py runserver"
echo ""
echo "For WebSocket support:"
echo "   daphne -b 0.0.0.0 -p 8000 smart_library.asgi:application"
echo ""
echo "The application will be available at: http://localhost:8000"
echo ""
echo "📖 For more information, see DJANGO_CONVERSION_GUIDE.md"

