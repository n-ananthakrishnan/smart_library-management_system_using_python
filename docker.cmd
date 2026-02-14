@echo off
REM SmartLib Docker Scripts for Windows

setlocal enabledelayedexpansion

if "%1"=="" goto help
if "%1"=="help" goto help
if "%1"=="build" goto build
if "%1"=="up" goto up
if "%1"=="down" goto down
if "%1"=="logs" goto logs
if "%1"=="migrate" goto migrate
if "%1"=="setup" goto setup
if "%1"=="prod-up" goto prod-up
if "%1"=="prod-down" goto prod-down
if "%1"=="db-backup" goto db-backup
if "%1"=="db-restore" goto db-restore

echo Unknown command: %1
goto help

:help
echo Smart Library Management System - Docker Commands
echo.
echo Usage: docker.cmd COMMAND
echo.
echo Commands:
echo   build           - Build Docker images
echo   up              - Start all services
echo   down            - Stop all services
echo   logs            - View logs
echo   migrate         - Run migrations
echo   setup           - Complete setup (build + up + migrate)
echo   prod-up         - Start production services
echo   prod-down       - Stop production services
echo   db-backup       - Backup database
echo   db-restore      - Restore database
echo   help            - Show this help message
echo.
echo After running 'setup', access:
echo   Web: http://localhost:8000
echo   Admin: http://localhost:8000/admin
goto end

:build
echo Building Docker images...
docker-compose build
goto end

:up
echo Starting services...
docker-compose up -d
echo.
echo Services started!
echo Web: http://localhost:8000
echo Admin: http://localhost:8000/admin
goto end

:down
echo Stopping services...
docker-compose down
goto end

:logs
echo Showing logs...
docker-compose logs -f
goto end

:migrate
echo Running migrations...
docker-compose exec web python manage.py migrate
goto end

:setup
echo Building Docker images...
docker-compose build
echo.
echo Starting services...
docker-compose up -d
echo.
echo Running migrations...
docker-compose exec web python manage.py migrate
echo.
echo Setup complete!
echo Web: http://localhost:8000
echo Admin: http://localhost:8000/admin
goto end

:prod-up
echo Starting production services...
docker-compose -f docker-compose.prod.yml up -d
echo Production services started!
goto end

:prod-down
echo Stopping production services...
docker-compose -f docker-compose.prod.yml down
goto end

:db-backup
echo Backing up database...
for /f "tokens=2-4 delims=/ " %%a in ('date /t') do (set mydate=%%c%%a%%b)
for /f "tokens=1-2 delims=/:" %%a in ('time /t') do (set mytime=%%a%%b)
docker-compose exec db pg_dump -U postgres smartlib > backup-%mydate%-%mytime%.sql
echo Database backed up!
goto end

:db-restore
if "%2"=="" (
    echo Usage: docker.cmd db-restore filename.sql
    goto end
)
echo Restoring database from %2...
docker-compose exec -T db psql -U postgres smartlib < %2
echo Database restored!
goto end

:end
endlocal
