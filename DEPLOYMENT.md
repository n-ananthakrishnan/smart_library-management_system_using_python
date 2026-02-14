# Deployment Guide

This guide covers deploying the Smart Library Management System to different environments.

## 🏠 Local Development

### Requirements
- Python 3.8+
- Virtual environment
- ~500MB disk space for database and uploads

### Setup Steps

```bash
# Clone and navigate
git clone <repo-url>
cd smart-library-management

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env .env.local
# Edit .env.local with your settings

# Initialize database
python -c "from app import app, db; app.app_context().push(); db.create_all()"

# Run development server
python app.py
```

The application will be available at `http://localhost:5000`

### Development Configuration

```env
FLASK_ENV=development
DEBUG=True
SECRET_KEY=dev-key-not-for-production
DATABASE_URL=sqlite:///library_dev.db
ENABLE_BARCODE_SCANNING=True
```

## ☁️ Heroku Deployment

### Prerequisites
- Heroku account (free or paid)
- Heroku CLI installed
- PostgreSQL add-on (for production database)

### Deployment Steps

1. **Install Heroku CLI**
   ```bash
   # macOS with Homebrew
   brew tap heroku/brew && brew install heroku
   
   # Windows with chocolatey
   choco install heroku-cli
   
   # Or download from https://devcenter.heroku.com/articles/heroku-cli
   ```

2. **Login to Heroku**
   ```bash
   heroku login
   ```

3. **Create Procfile**
   ```bash
   echo "web: gunicorn app:app" > Procfile
   ```

4. **Create Heroku app**
   ```bash
   heroku create your-app-name
   ```

5. **Add PostgreSQL add-on**
   ```bash
   heroku addons:create heroku-postgresql:hobby-dev
   ```

6. **Set environment variables**
   ```bash
   # Generate secure secret key
   python -c "import secrets; print(secrets.token_hex(32))"
   
   # Set config vars
   heroku config:set FLASK_ENV=production
   heroku config:set DEBUG=False
   heroku config:set SECRET_KEY=your-generated-secret-key
   ```

7. **Deploy**
   ```bash
   git push heroku main
   ```

8. **Initialize database**
   ```bash
   heroku run python
   >>> from app import app, db
   >>> with app.app_context(): db.create_all()
   >>> exit()
   ```

9. **Access application**
   ```bash
   heroku open
   ```

### Monitoring
```bash
# View logs
heroku logs --tail

# Check app status
heroku ps

# Scale dynos if needed
heroku ps:scale web=2
```

## 🐳 Docker Deployment

### Prerequisites
- Docker installed
- Docker Compose (optional, for multi-container setup)

### Dockerfile

Create `Dockerfile` in project root:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create instance directory
RUN mkdir -p instance uploads

# Expose port
EXPOSE 5000

# Environment
ENV FLASK_APP=app.py
ENV PYTHONUNBUFFERED=1

# Run application
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "--timeout", "120", "app:app"]
```

### Docker Compose (with PostgreSQL)

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - DEBUG=False
      - DATABASE_URL=postgresql://library:password@db:5432/library
      - SECRET_KEY=change-this-to-a-secure-value
    depends_on:
      - db
    volumes:
      - ./instance:/app/instance
      - ./static/uploads:/app/static/uploads

  db:
    image: postgres:14-alpine
    environment:
      - POSTGRES_USER=library
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=library
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### Build and Run

```bash
# Build image
docker build -t smart-library:latest .

# Run with Docker
docker run -p 5000:5000 -e DATABASE_URL=sqlite:///library.db smart-library:latest

# Run with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f web

# Stop services
docker-compose down
```

## 🖥️ Traditional Server (Ubuntu/Debian)

### Prerequisites
- Ubuntu 20.04 or later
- Python 3.8+
- Nginx web server
- PostgreSQL 12+
- Supervisor for process management

### Installation

1. **Update system**
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

2. **Install dependencies**
   ```bash
   sudo apt install -y python3-pip python3-venv postgresql postgresql-contrib nginx supervisor
   ```

3. **Create application user**
   ```bash
   sudo useradd -m -s /bin/bash library
   su - library
   ```

4. **Clone application**
   ```bash
   git clone <repo-url> /home/library/smart-library
   cd /home/library/smart-library
   ```

5. **Setup Python environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt gunicorn
   ```

6. **Configure PostgreSQL**
   ```bash
   # As root/sudo
   sudo -u postgres psql << EOF
   CREATE DATABASE library;
   CREATE USER library WITH PASSWORD 'secure_password';
   ALTER ROLE library SET client_encoding TO 'utf8';
   ALTER ROLE library SET default_transaction_isolation TO 'read committed';
   ALTER ROLE library SET default_transaction_deferrable TO on;
   ALTER ROLE library SET default_transaction_read_only TO off;
   GRANT ALL PRIVILEGES ON DATABASE library TO library;
   \q
   EOF
   ```

7. **Create .env file**
   ```bash
   cat > /home/library/smart-library/.env << EOF
   FLASK_ENV=production
   DEBUG=False
   DATABASE_URL=postgresql://library:secure_password@localhost/library
   SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
   EOF
   
   chmod 600 .env
   ```

8. **Initialize database**
   ```bash
   source venv/bin/activate
   python3 -c "from app import app, db; app.app_context().push(); db.create_all()"
   ```

### Nginx Configuration

Create `/etc/nginx/sites-available/smart-library`:

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # SSL certificates (use Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Gzip compression
    gzip on;
    gzip_types text/plain text/css text/javascript application/json;
    gzip_min_length 1000;

    # Client upload limit
    client_max_body_size 16M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Static files
    location /static/ {
        alias /home/library/smart-library/static/;
        expires 30d;
    }

    # Uploads
    location /uploads/ {
        alias /home/library/smart-library/static/uploads/;
        expires 7d;
    }
}
```

Enable the site:
```bash
sudo ln -s /etc/nginx/sites-available/smart-library /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Supervisor Configuration

Create `/etc/supervisor/conf.d/smart-library.conf`:

```ini
[program:smart-library]
command=/home/library/smart-library/venv/bin/gunicorn -w 4 -b 127.0.0.1:8000 app:app
directory=/home/library/smart-library
user=library
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/library/gunicorn.log
```

Start the service:
```bash
sudo mkdir -p /var/log/library
sudo chown library:library /var/log/library
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start smart-library
```

### Setup SSL with Let's Encrypt

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot certonly --nginx -d yourdomain.com -d www.yourdomain.com
```

## 🔒 Production Security Checklist

- [ ] Change default `SECRET_KEY` to a cryptographically secure random value
- [ ] Set `DEBUG=False` in production
- [ ] Use HTTPS with valid SSL certificate
- [ ] Configure CORS properly (restrict origins)
- [ ] Enable CSRF protection on all forms
- [ ] Use strong database password
- [ ] Regular database backups
- [ ] Monitor and log application errors
- [ ] Implement rate limiting
- [ ] Keep dependencies updated
- [ ] Use environment variables for sensitive data
- [ ] Enable user input validation
- [ ] Setup web application firewall (WAF)
- [ ] Configure database access control
- [ ] Implement user authentication hardening

## 📈 Performance Optimization

### Database
```python
# Use connection pooling
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_size': 10,
    'pool_recycle': 3600,
    'pool_pre_ping': True,
}
```

### Caching
- Implement Redis for session storage
- Cache static assets
- Use database query optimization

### Monitoring
- Setup application performance monitoring (APM)
- Configure error tracking (Sentry)
- Monitor resource usage and response times

## 🔄 Continuous Deployment (CI/CD)

### GitHub Actions Example

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Production

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Run tests
        run: |
          python -m pip install -r requirements.txt
          python -m pytest
      
      - name: Deploy to Heroku
        uses: AkhileshNS/heroku-deploy@v3.12.12
        with:
          heroku_api_key: ${{ secrets.HEROKU_API_KEY }}
          heroku_app_name: ${{ secrets.HEROKU_APP_NAME }}
          heroku_email: ${{ secrets.HEROKU_EMAIL }}
```

## 📊 Monitoring & Maintenance

### Logs
```bash
# Application logs
tail -f /var/log/library/gunicorn.log

# System logs
journalctl -u nginx -f
sudo journalctl -u supervisor -f
```

### Database Maintenance
```bash
# Backup
pg_dump library > library_backup.sql

# Restore
psql library < library_backup.sql
```

### Health Checks
Create a simple health endpoint for monitoring:
```python
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'version': '2.0'}), 200
```

## 🆘 Troubleshooting

### Application Won't Start
```bash
# Check logs
supervisorctl tail smart-library

# Verify configuration
python -c "from app import app; print(app.config)"

# Check database connection
psql -U library -d library -c "SELECT 1"
```

### High Memory Usage
- Implement connection pooling
- Optimize database queries
- Use caching mechanisms
- Monitor open file descriptors

### WebSocket Connection Issues
- Verify Socket.IO is properly configured
- Check firewall settings for WebSocket ports
- Enable debugging in Socket.IO client

---

For additional support, see README.md or open an issue on GitHub.
