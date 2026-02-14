@echo off
REM Smart Library Management System - Django Setup Script (Windows)
REM Converts Flask to Django and initializes the project

setlocal enabledelayedexpansion

echo.
echo 🚀 Smart Library Management System - Django Setup
echo ==================================================
echo.

REM Check Python version
echo 📋 Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo    Please install Python 3.8+ from https://www.python.org
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✓ Python %PYTHON_VERSION% found
echo.

REM Create virtual environment
echo 🔧 Setting up virtual environment...
if not exist "venv" (
    python -m venv venv
    echo ✓ Virtual environment created
) else (
    echo ✓ Virtual environment already exists
)
echo.

REM Activate virtual environment
call venv\Scripts\activate.bat
echo ✓ Virtual environment activated
echo.

REM Upgrade pip
echo 📦 Upgrading pip...
python -m pip install --upgrade pip setuptools wheel >nul 2>&1
echo ✓ pip upgraded
echo.

REM Install dependencies
echo 📦 Installing Django dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)
echo ✓ Dependencies installed
echo.

REM Create .env file if it doesn't exist
echo ⚙️  Configuring environment...
if not exist ".env" (
    echo ℹ️  Creating .env for Django...
    (
        echo SECRET_KEY=dev-key-change-in-production
        echo DEBUG=True
        echo ALLOWED_HOSTS=localhost,127.0.0.1
        echo DATABASE_URL=sqlite:///db.sqlite3
    ) > .env
    echo ✓ .env created
) else (
    echo ✓ .env already exists
)
echo.

REM Create necessary directories
echo 📁 Creating required directories...
if not exist "media\profiles" mkdir media\profiles
if not exist "media\book_covers" mkdir media\book_covers
echo ✓ Directories created
echo.

REM Run migrations
echo 🗄️  Running Django migrations...
python manage.py migrate
if errorlevel 1 (
    echo ❌ Migration failed
    pause
    exit /b 1
)
echo ✓ Migrations completed
echo.

REM Create sample data
echo 👥 Creating sample data...
python manage.py init_db
echo ✓ Sample data created
echo.

REM Collect static files
echo 📦 Collecting static files...
python manage.py collectstatic --noinput
echo ✓ Static files collected
echo.

echo ✨ Setup complete!
echo.
echo 🚀 To start the application, run:
echo    venv\Scripts\activate.bat
echo    python manage.py runserver
echo.
echo For WebSocket support:
echo    daphne -b 0.0.0.0 -p 8000 smart_library.asgi:application
echo.
echo The application will be available at: http://localhost:8000
echo.
echo 📖 For more information, see DJANGO_CONVERSION_GUIDE.md
echo.
pause
