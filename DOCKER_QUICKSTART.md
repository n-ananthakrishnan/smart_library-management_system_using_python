# Docker Quick Start Guide

## ⚡ 5-Minute Setup

### Prerequisites
- Docker Desktop (Windows/Mac) or Docker Engine (Linux)
- Docker Compose

### Step 1: Prepare Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env if needed (optional for development)
# nano .env
```

### Step 2: Start Services

**On Linux/Mac:**
```bash
# One-command setup
make init

# Or manually:
docker-compose build
docker-compose up -d
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
```

**On Windows (PowerShell):**
```bash
# Using the provided script
.\docker.cmd setup

# Or manually:
docker-compose build
docker-compose up -d
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
```

### Step 3: Access the Application

- **Web Interface**: http://localhost:8000
- **Admin Panel**: http://localhost:8000/admin
- **Book List**: http://localhost:8000/books/

## 🍃 Development Workflow

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f web
docker-compose logs -f db
docker-compose logs -f nginx
```

### Run Django Commands
```bash
# Migrations
docker-compose exec web python manage.py migrate

# Create new app
docker-compose exec web python manage.py startapp myapp

# Django shell
docker-compose exec web python manage.py shell

# Run tests
docker-compose exec web python manage.py test
```

### Database Access
```bash
# Connect to PostgreSQL
docker-compose exec db psql -U postgres -d smartlib

# Useful PostgreSQL commands:
# \dt                    - List tables
# \d table_name          - Describe table
# SELECT * FROM table;   - Query data
# \q                     - Exit
```

### Code Changes
- Edit files directly, they'll auto-reload in development mode
- Static files are watched by Django dev server
- For requirements.txt changes:
  ```bash
  docker-compose build
  docker-compose up -d
  ```

## 📦 Production Deployment

### Step 1: Security Configuration
```bash
# Copy environment file
cp .env.example .env.prod

# Edit with production values
nano .env.prod
```

**Critical settings:**
```env
DEBUG=False
SECRET_KEY=<generate-strong-key>
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DB_PASSWORD=<strong-password>
ADMIN_PASSWORD=<strong-password>
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

### Step 2: Generate Secret Key
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### Step 3: Setup SSL (Let's Encrypt)
```bash
# Create SSL directory
mkdir -p ssl

# Generate certificate
docker run -it --rm -v $(pwd)/ssl:/etc/letsencrypt certbot/certbot certonly \
  --standalone \
  -d yourdomain.com \
  -d www.yourdomain.com
```

### Step 4: Start Production
```bash
# Using Makefile (Linux/Mac)
make prod-init

# Or manually
docker-compose -f docker-compose.prod.yml up -d
```

### Step 5: Verify
```bash
# Check status
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Health check
curl https://yourdomain.com/health/
```

## 🔧 Common Tasks

### Backup Database
```bash
# Development
docker-compose exec db pg_dump -U postgres smartlib > backup.sql

# Production
docker-compose -f docker-compose.prod.yml exec db pg_dump -U postgres smartlib > backup.sql
```

### Restore Database
```bash
# Development
docker-compose exec -T db psql -U postgres smartlib < backup.sql

# Production
docker-compose -f docker-compose.prod.yml exec -T db psql -U postgres smartlib < backup.sql
```

### Update Dependencies
```bash
# Install new package
pip install new_package
pip freeze > requirements.txt

# Rebuild container
docker-compose build
docker-compose up -d
```

### View System Resources
```bash
docker stats
```

### Clean Everything
```bash
# Stop and remove all containers and volumes
docker-compose down -v

# WARNING: This deletes all data!
```

## 🐛 Troubleshooting

### Services won't start
```bash
# Check logs
docker-compose logs

# Check system resources
docker ps
docker system df
```

### Database connection error
```bash
# Verify database is healthy
docker-compose ps
# Should show "healthy" for db service

# Try reconnecting
docker-compose exec db psql -U postgres -d smartlib
```

### Port already in use
```bash
# Find process using the port (Linux/Mac)
lsof -i :8000
kill -9 <PID>

# Or change ports in docker-compose.yml
```

### Static files not loading
```bash
# Collect static files
docker-compose exec web python manage.py collectstatic --noinput --clear

# Restart Nginx
docker-compose restart nginx
```

### Migrations failing
```bash
# Check migration status
docker-compose exec web python manage.py showmigrations

# Rollback if needed
docker-compose exec web python manage.py migrate library 0001

# Re-migrate
docker-compose exec web python manage.py migrate
```

## 📊 Monitoring

### Health Checks
```bash
# Verify application health
curl http://localhost:8000/health/

# Check each service
docker-compose ps
```

### Logs Monitoring
```bash
# Real-time logs
docker-compose logs -f

# Filter logs
docker-compose logs web --tail=50
docker-compose logs --since=10m
```

### Performance Monitoring
```bash
# Container stats
docker stats

# System info
docker system info
```

## 🚀 Advanced Usage

### Scale Services
```bash
# Run multiple web instances (requires Docker Swarm or Kubernetes)
docker-compose up -d --scale web=3
```

### Custom Configuration
Edit `docker-compose.yml` or `docker-compose.prod.yml`:
- Change port mappings
- Adjust resource limits
- Add environment variables
- Mount additional volumes

### Use Different Database
In `.env`:
```env
DATABASE_URL=postgresql://user:pass@db:5432/dbname
```

### Enable Redis Caching
Already included! Configure in Django settings.

## 📚 Interactive Help

### Show Available Commands
```bash
# Linux/Mac
make help

# Windows
docker.cmd help
```

### Full Documentation
See [DOCKER.md](DOCKER.md) for comprehensive documentation.

## 🆘 Getting Help

1. Check [DOCKER.md](DOCKER.md) for detailed troubleshooting
2. Review Docker Compose logs
3. Check Django documentation
4. Verify environment variables in `.env`

## 💡 Tips & Tricks

### Development Speed Tips
- Use `docker-compose exec` instead of SSH
- Enable auto-reload in Django (already configured)
- Use VS Code Remote - Containers extension
- Mount your local directory for hot-reload

### Security Tips  
- Never commit `.env` files
- Use strong secrets for production
- Enable SSL/TLS in production
- Regularly backup database
- Keep images updated

### Performance Tips
- Use production compose file for production
- Set appropriate worker counts
- Enable Redis caching
- Use Nginx for static files
- Monitor with `docker stats`

## 📋 Checklist for Production

- [ ] Change SECRET_KEY
- [ ] Set DEBUG=False
- [ ] Configure ALLOWED_HOSTS
- [ ] Setup SSL certificate
- [ ] Configure strong database password
- [ ] Setup email configuration
- [ ] Configure backup strategy
- [ ] Setup monitoring
- [ ] Configure firewall rules
- [ ] Test database backup/restore
- [ ] Review security settings
- [ ] Setup log rotation

## 🎯 Common Workflows

### Deploy New Code
```bash
git pull
docker-compose build
docker-compose down
docker-compose up -d
docker-compose exec web python manage.py migrate
```

### Daily Maintenance
```bash
# Check health
docker-compose ps

# Review logs
docker-compose logs --since=1h

# Backup database
docker-compose exec db pg_dump -U postgres smartlib > backup.sql
```

### Update Python Dependencies
```bash
pip install --upgrade package_name
pip freeze > requirements.txt
docker-compose build
docker-compose restart web
```

---

**Happy Developing! 🚀**

For more information, see [DOCKER.md](DOCKER.md)
