# Docker Deployment - Complete Guide

## 🎯 What You Get

A production-ready Docker setup for the Smart Library Management System with:

- **Development environment** with auto-reload
- **Production environment** with Nginx, PostgreSQL, and Redis
- **Database persistence** with automated backups
- **Caching layer** with Redis
- **WebSocket support** via Django Channels
- **Static file serving** via Nginx
- **SSL/TLS ready** configuration
- **Health checks** for all services
- **Logging and monitoring** capabilities

## 📦 Docker Files Overview

| File | Purpose |
|------|---------|
| `Dockerfile` | Multi-stage Docker build for optimized images |
| `docker-compose.yml` | Development setup (PostgreSQL, Redis, Django, Nginx) |
| `docker-compose.prod.yml` | Production setup with security hardening |
| `entrypoint.sh` | Container initialization and setup script |
| `nginx.conf` | Nginx reverse proxy configuration |
| `.dockerignore` | Files excluded from Docker build |
| `.env.example` | Environment variables template |
| `Makefile` | Commands for Linux/Mac users |
| `docker.cmd` | Commands for Windows users |
| `install.sh` | Automated installation script |

## 🚀 Quick Start (Choose One)

### Option 1: Automated Installation (Recommended)

**Linux/Mac:**
```bash
chmod +x install.sh
./install.sh
```

**Windows (PowerShell):**
```powershell
# Run install.cmd if available, or:
docker-compose build
docker-compose up -d
docker-compose exec web python manage.py migrate --noinput
docker-compose exec web python manage.py createsuperuser --noinput --username admin --email admin@smartlib.local
```

### Option 2: Manual Setup (Linux/Mac with Make)

```bash
make init
```

### Option 3: Manual Setup (Windows)

```powershell
docker.cmd setup
```

### Option 4: Step-by-Step

```bash
# 1. Setup environment
cp .env.example .env

# 2. Build and start
docker-compose build
docker-compose up -d

# 3. Run migrations
docker-compose exec web python manage.py migrate

# 4. Create superuser
docker-compose exec web python manage.py createsuperuser

# 5. Access the app
# Open: http://localhost:8000
# Admin: http://localhost:8000/admin
```

## 📋 Available Commands

### Using Makefile (Linux/Mac)
```bash
make help              # Show all available commands
make up                # Start services
make down              # Stop services
make logs              # View logs
make migrate           # Run migrations
make shell             # Django shell
make test              # Run tests
make db-backup         # Backup database
make db-restore FILE=backup.sql  # Restore database
```

### Using docker.cmd (Windows)
```batch
docker.cmd help        # Show all available commands
docker.cmd up          # Start services
docker.cmd down        # Stop services
docker.cmd setup       # Complete setup
docker.cmd db-backup   # Backup database
```

### Using docker-compose directly
```bash
# Development
docker-compose ps              # List running services
docker-compose logs -f         # View logs
docker-compose exec web /bin/bash  # Shell into web container
docker-compose down            # Stop all services

# Production
docker-compose -f docker-compose.prod.yml up -d
```

## 🎛️ Configuration

### Environment Variables (.env)

Create `.env` from template:
```bash
cp .env.example .env
nano .env
```

**Key variables:**

| Variable | Default | Description |
|----------|---------|-------------|
| `DEBUG` | True | Turn off in production |
| `SECRET_KEY` | dev-key | Django secret key (CHANGE FOR PROD) |
| `ALLOWED_HOSTS` | localhost | Comma-separated allowed hosts |
| `DB_PASSWORD` | postgres | PostgreSQL password |
| `ADMIN_PASSWORD` | admin123 | Admin user password |
| `SECURE_SSL_REDIRECT` | False | Force HTTPS (enable in prod) |

## 🏠 Service Access

| Service | URL | Port | Docker | Notes |
|---------|-----|------|--------|-------|
| Web Interface | http://localhost:8000 | 8000 | web | Django app |
| Admin Panel | http://localhost:8000/admin | 8000 | web | Django admin |
| PostgreSQL | localhost:5432 | 5432 | db | Database |
| Redis | localhost:6379 | 6379 | redis | Cache |
| Nginx | http://localhost | 80 | nginx | Reverse proxy |

## 📦 Services Included

### PostgreSQL (Database)
- Latest stable version (15)
- Automatic initialization
- Data persistence in volumes
- Backup capability

### Redis (Cache)
- Latest stable version (7)
- Session/cache storage
- Optional: persistence enabled
- Memory-efficient

### Django Application
- Python 3.13
- All dependencies installed
- Auto-migrations on startup
- Hot reload in development
- Gunicorn in production

### Nginx (Reverse Proxy)
- SSL/TLS support ready
- Static file serving
- WebSocket support
- Gzip compression
- Health check endpoint

## 🔐 Security Features

### Development
- ✅ CSRF protection
- ✅ XSS protection
- ✅ SQL injection prevention
- ✅ Secure password hashing

### Production
- ✅ All above
- ✅ HTTPS enforcement
- ✅ Secure cookies
- ✅ Security headers
- ✅ Network isolation
- ✅ PostgreSQL (not SQLite)

## 📊 Common Tasks

### Check Service Status
```bash
docker-compose ps
```

### View Logs
```bash
docker-compose logs -f          # All services
docker-compose logs -f web      # Just web app
```

### Access Database
```bash
docker-compose exec db psql -U postgres -d smartlib
```

### Django Management Commands
```bash
# Migrations
docker-compose exec web python manage.py migrate

# Create app
docker-compose exec web python manage.py startapp myapp

# Shell
docker-compose exec web python manage.py shell

# Tests
docker-compose exec web python manage.py test
```

### Backup Database
```bash
docker-compose exec db pg_dump -U postgres smartlib > backup.sql
```

### Restore Database
```bash
docker-compose exec -T db psql -U postgres smartlib < backup.sql
```

## 🚀 Production Deployment

### 1. Prepare Production Environment
```bash
cp .env.example .env.prod
# Edit with production values:
# - DEBUG=False
# - SECRET_KEY=<generate new>
# - ALLOWED_HOSTS=yourdomain.com
# - DB_PASSWORD=<strong password>
# - SECURE_SSL_REDIRECT=True
```

### 2. Setup SSL Certificate
```bash
mkdir -p ssl
docker run -it --rm -v $(pwd)/ssl:/etc/letsencrypt certbot/certbot certonly \
  --standalone \
  -d yourdomain.com \
  -d www.yourdomain.com
```

### 3. Start Production Services
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### 4. Verify Deployment
```bash
docker-compose -f docker-compose.prod.yml ps
curl https://yourdomain.com/health/
```

## 🐛 Troubleshooting

### Services Won't Start
```bash
# Check logs
docker-compose logs

# Check Docker daemon
docker ps

# Rebuild without cache
docker-compose build --no-cache
docker-compose up -d
```

### Database Connection Issues
```bash
# Check if db service is healthy
docker-compose ps db

# Try connecting manually
docker-compose exec db psql -U postgres -d smartlib
```

### Port Already in Use
```bash
# Find process using port (Linux/Mac)
lsof -i :8000
kill -9 <PID>

# Or change port in docker-compose.yml
```

### Static Files Not Found
```bash
# Collect static files
docker-compose exec web python manage.py collectstatic --noinput --clear

# Restart Nginx
docker-compose restart nginx
```

See [DOCKER.md](DOCKER.md) for comprehensive troubleshooting.

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| [DOCKER.md](DOCKER.md) | Complete Docker guide (700+ lines) |
| [DOCKER_QUICKSTART.md](DOCKER_QUICKSTART.md) | Quick reference guide |
| [DOCKER_SETUP_SUMMARY.md](DOCKER_SETUP_SUMMARY.md) | Setup overview |

## 🎯 Next Steps

1. **Run quick start**: `make init` or `docker.cmd setup`
2. **Access application**: http://localhost:8000
3. **Read documentation**: See DOCKER_QUICKSTART.md
4. **Deploy to production**: Follow DOCKER.md

## 💡 Best Practices

### Development
- ✅ Use docker-compose.yml (includes auto-reload)
- ✅ Edit .env for configuration
- ✅ Check logs frequently: `docker-compose logs -f`
- ✅ Use `docker-compose exec` for management commands

### Production
- ✅ Use docker-compose.prod.yml
- ✅ Set DEBUG=False
- ✅ Generate new SECRET_KEY
- ✅ Use strong database password
- ✅ Setup SSL/TLS certificate
- ✅ Configure firewall (only 80/443)
- ✅ Regular database backups
- ✅ Monitor logs and resources

## 🔗 Additional Resources

- [Docker Docs](https://docs.docker.com/)
- [Docker Compose Docs](https://docs.docker.com/compose/)
- [Django Docs](https://docs.djangoproject.com/)
- [Nginx Docs](https://nginx.org/docs/)

## ❓ FAQ

**Q: Can I use SQLite with Docker?**
A: Yes, SQLite works but PostgreSQL is recommended for production.

**Q: How do I update dependencies?**
A: Edit requirements.txt, then `docker-compose build` and `docker-compose restart`.

**Q: How do I access the database?**
A: Use `docker-compose exec db psql -U postgres -d smartlib`

**Q: Can I run multiple instances?**
A: Yes, with Docker Swarm or Kubernetes.

**Q: Is it production-ready?**
A: The docker-compose.prod.yml is designed for production. Add your own monitoring/backup services as needed.

## 🎉 You're Ready!

Your Docker setup is complete. Start with:

```bash
# Linux/Mac
make init

# Windows
docker.cmd setup

# Then visit: http://localhost:8000
```

For detailed information, see [DOCKER_QUICKSTART.md](DOCKER_QUICKSTART.md) or [DOCKER.md](DOCKER.md).

---

**Questions?** Check the documentation or run `make help` / `docker.cmd help`
