# Docker Setup Guide for SmartLib

This guide explains how to containerize and run the Smart Library Management System using Docker and Docker Compose.

## Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- Git

## Project Structure

```
smartlib/
├── Dockerfile                 # Multi-stage Docker build
├── docker-compose.yml         # Development setup
├── docker-compose.prod.yml    # Production setup
├── entrypoint.sh             # Container initialization script
├── nginx.conf                # Nginx reverse proxy config
├── .dockerignore             # Files to exclude from Docker build
├── .env.example              # Environment variables template
└── ... (rest of Django project)
```

## Development Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd smart_library-management
```

### 2. Create Environment File

```bash
cp .env.example .env
```

Edit `.env` with your settings:
```env
DEBUG=True
SECRET_KEY=your-development-secret-key
DB_PASSWORD=your-db-password
ADMIN_PASSWORD=your-admin-password
```

### 3. Build and Start Containers

```bash
# Build images
docker-compose build

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f web
```

### 4. Access the Application

- **Web Interface**: http://localhost:8000
- **Admin Panel**: http://localhost:8000/admin
- **API**: http://localhost:8000/api/

**Default Credentials** (from .env):
- Username: admin
- Password: (set in ADMIN_PASSWORD)

## Production Setup

### 1. Prepare Production Environment

```bash
cp .env.example .env.production
```

Edit `.env.production` with production values:
```env
DEBUG=False
SECRET_KEY=<generate-a-new-secure-key>
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DB_PASSWORD=<strong-postgres-password>
ADMIN_PASSWORD=<strong-admin-password>
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

### 2. Generate Django Secret Key

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 3. Start Production Services

```bash
# Use production compose file
docker-compose -f docker-compose.prod.yml up -d

# View logs
docker-compose -f docker-compose.prod.yml logs -f web
```

### 4. SSL/TLS Setup (Let's Encrypt)

Install Certbot and generate certificates:

```bash
mkdir -p ssl
docker run -it --rm -v $(pwd)/ssl:/etc/letsencrypt certbot/certbot certonly \
  --standalone \
  -d yourdomain.com \
  -d www.yourdomain.com
```

## Docker Services

### PostgreSQL Database
- **Container**: smartlib_db
- **Port**: 5432 (internal)
- **Volume**: postgres_data
- **Backup Volume**: postgres_backups

### Redis Cache
- **Container**: smartlib_redis
- **Port**: 6379 (internal)
- **Volume**: redis_data
- **Features**: Persistence enabled

### Django Web Application
- **Container**: smartlib_web
- **Port**: 8000 (development), exposed via Nginx (production)
- **ASGI Server**: Daphne (development) / Gunicorn (production)
- **Volumes**: static files, media, logs

### Nginx Web Server
- **Container**: smartlib_nginx
- **Ports**: 80 (HTTP), 443 (HTTPS)
- **Config**: nginx.conf
- **Features**: Reverse proxy, static file serving, WebSocket support

## Common Commands

### Development Commands

```bash
# View logs
docker-compose logs -f

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Run shell
docker-compose exec web python manage.py shell

# Run tests
docker-compose exec web python manage.py test

# Collect static files
docker-compose exec web python manage.py collectstatic --noinput

# Stop services
docker-compose down

# Remove all volumes (caution!)
docker-compose down -v

# Rebuild without cache
docker-compose build --no-cache
```

### Production Commands

```bash
# Same as above but with prod file
docker-compose -f docker-compose.prod.yml logs -f

# Database backup
docker-compose -f docker-compose.prod.yml exec db pg_dump \
  -U postgres smartlib > backup-$(date +%Y%m%d-%H%M%S).sql

# Database restore
docker-compose -f docker-compose.prod.yml exec -T db psql \
  -U postgres smartlib < backup.sql
```

## Environment Variables

### Core Django Settings
- `DEBUG`: Turn off in production (default: False)
- `DJANGO_SETTINGS_MODULE`: Django settings module (default: smart_library.settings)
- `SECRET_KEY`: Django secret key (MUST change in production)
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts

### Database Configuration
- `DB_ENGINE`: Database backend (default: django.db.backends.postgresql)
- `DB_NAME`: Database name (default: smartlib)
- `DB_USER`: Database user (default: postgres)
- `DB_PASSWORD`: Database password
- `DB_HOST`: Database host (default: db)
- `DB_PORT`: Database port (default: 5432)

### Redis Configuration
- `REDIS_URL`: Redis connection URL (default: redis://redis:6379/0)

### Features
- `ENABLE_BARCODE_SCANNING`: Enable barcode scanning (default: True)
- `ENABLE_QR_CODE`: Enable QR code generation (default: True)

### Security Settings
- `SECURE_SSL_REDIRECT`: Force HTTPS redirect (default: False)
- `SESSION_COOKIE_SECURE`: Secure session cookies (default: False)
- `CSRF_COOKIE_SECURE`: Secure CSRF cookies (default: False)

## Health Checks

Each service includes health checks:

```bash
# Check service health
docker-compose ps

# Manual health check
curl http://localhost:8000/health/
```

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker-compose logs web

# Verify network
docker network ls
docker network inspect smartlib_network
```

### Database Connection Issues

```bash
# Check database service
docker-compose logs db

# Connect to database manually
docker-compose exec db psql -U postgres -d smartlib
```

### Static Files Not Loading

```bash
# Recreate static files
docker-compose exec web python manage.py collectstatic --noinput --clear

# Restart Nginx
docker-compose restart nginx
```

### Permission Issues

```bash
# Fix volume permissions
docker-compose exec web chmod -R 755 /app/staticfiles
docker-compose exec web chmod -R 755 /app/media
```

## Backup and Restore

### Database Backup

```bash
# Development
docker-compose exec db pg_dump -U postgres smartlib > backup.sql

# Production
docker-compose -f docker-compose.prod.yml exec db pg_dump \
  -U postgres smartlib > backup.sql
```

### Database Restore

```bash
# Development
docker-compose exec -T db psql -U postgres smartlib < backup.sql

# Production
docker-compose -f docker-compose.prod.yml exec -T db \
  psql -U postgres smartlib < backup.sql
```

## Docker Registry Push

### Build and Push to Docker Hub

```bash
# Login to Docker Hub
docker login

# Tag image
docker tag smartlib_web username/smartlib:latest

# Push image
docker push username/smartlib:latest

# Pull and run
docker pull username/smartlib:latest
docker-compose pull
docker-compose up
```

## Performance Optimization

### For Production

1. **Use production compose file**: `docker-compose.prod.yml`
2. **Set appropriate worker count**: Adjust gunicorn workers based on CPU cores
3. **Enable Redis caching**: Already configured in production
4. **Use Nginx compression**: Enabled in nginx.conf
5. **Monitor container resources**: `docker stats`

```bash
# Monitor running containers
docker stats

# Set resource limits
# Edit docker-compose.prod.yml and add:
# deploy:
#   resources:
#     limits:
#       cpus: '2'
#       memory: 1G
#     reservations:
#       cpus: '1'
#       memory: 512M
```

## Security Best Practices

1. **Change default passwords** in .env
2. **Use strong SECRET_KEY**: Generate with Django utility
3. **Enable SSL/TLS** in production
4. **Use environment variables** for sensitive data
5. **Regular backups** of database
6. **Keep images updated**: `docker-compose pull`
7. **Limit port exposure**: Only expose 80/443 to internet
8. **Use network isolation**: Services communicate via Docker network

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Build and Deploy

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Build Docker image
        run: docker-compose build
      - name: Push to registry
        run: |
          echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
          docker-compose push
```

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Django Deployment with Docker](https://docs.djangoproject.com/en/4.2/howto/deployment/)
- [Nginx Configuration](https://nginx.org/en/docs/)

## Support

For issues or questions, please refer to the main README.md or create an issue on the repository.
