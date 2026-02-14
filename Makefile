.PHONY: help build up down logs migrate shell test clean collectstatic createsuperuser backup restore push-registry

# Variables
DOCKER_COMPOSE := docker-compose
DOCKER_COMPOSE_PROD := docker-compose -f docker-compose.prod.yml

# Default target
help:
	@echo "Smart Library Management System - Docker Commands"
	@echo ""
	@echo "Development Commands:"
	@echo "  make build              - Build Docker images"
	@echo "  make up                 - Start all services"
	@echo "  make down               - Stop all services"
	@echo "  make logs               - View logs"
	@echo "  make logs-web           - View web container logs"
	@echo "  make migrate            - Run migrations"
	@echo "  make shell              - Django shell"
	@echo "  make test               - Run tests"
	@echo "  make createsuperuser    - Create admin user"
	@echo "  make collectstatic      - Collect static files"
	@echo "  make clean              - Remove all containers and volumes"
	@echo ""
	@echo "Production Commands:"
	@echo "  make prod-build         - Build for production"
	@echo "  make prod-up            - Start production services"
	@echo "  make prod-down          - Stop production services"
	@echo "  make prod-logs          - View production logs"
	@echo ""
	@echo "Database Commands:"
	@echo "  make db-shell           - Connect to PostgreSQL"
	@echo "  make db-backup          - Backup database"
	@echo "  make db-restore FILE=backup.sql - Restore database"
	@echo ""
	@echo "Registry Commands:"
	@echo "  make push-registry      - Push image to Docker Hub"
	@echo ""

# Development Commands
build:
	$(DOCKER_COMPOSE) build

up:
	$(DOCKER_COMPOSE) up -d
	@echo "Services started!"
	@echo "Web: http://localhost:8000"
	@echo "Admin: http://localhost:8000/admin"

down:
	$(DOCKER_COMPOSE) down

logs:
	$(DOCKER_COMPOSE) logs -f

logs-web:
	$(DOCKER_COMPOSE) logs -f web

logs-db:
	$(DOCKER_COMPOSE) logs -f db

logs-nginx:
	$(DOCKER_COMPOSE) logs -f nginx

migrate:
	$(DOCKER_COMPOSE) exec web python manage.py migrate

shell:
	$(DOCKER_COMPOSE) exec web python manage.py shell

test:
	$(DOCKER_COMPOSE) exec web python manage.py test

createsuperuser:
	$(DOCKER_COMPOSE) exec web python manage.py createsuperuser

collectstatic:
	$(DOCKER_COMPOSE) exec web python manage.py collectstatic --noinput

clean:
	$(DOCKER_COMPOSE) down -v
	@echo "All containers and volumes removed!"

# Production Commands
prod-build:
	$(DOCKER_COMPOSE_PROD) build

prod-up:
	$(DOCKER_COMPOSE_PROD) up -d
	@echo "Production services started!"

prod-down:
	$(DOCKER_COMPOSE_PROD) down

prod-logs:
	$(DOCKER_COMPOSE_PROD) logs -f

prod-logs-web:
	$(DOCKER_COMPOSE_PROD) logs -f web

prod-logs-nginx:
	$(DOCKER_COMPOSE_PROD) logs -f nginx

# Database Commands
db-shell:
	$(DOCKER_COMPOSE) exec db psql -U postgres -d smartlib

db-backup:
	$(DOCKER_COMPOSE) exec db pg_dump -U postgres smartlib > backup-$$(date +%Y%m%d-%H%M%S).sql
	@echo "Database backed up!"

db-restore:
	@if [ -z "$(FILE)" ]; then echo "Usage: make db-restore FILE=backup.sql"; exit 1; fi
	$(DOCKER_COMPOSE) exec -T db psql -U postgres smartlib < $(FILE)
	@echo "Database restored from $(FILE)!"

prod-db-backup:
	$(DOCKER_COMPOSE_PROD) exec db pg_dump -U postgres smartlib > backup-prod-$$(date +%Y%m%d-%H%M%S).sql
	@echo "Production database backed up!"

prod-db-restore:
	@if [ -z "$(FILE)" ]; then echo "Usage: make prod-db-restore FILE=backup.sql"; exit 1; fi
	$(DOCKER_COMPOSE_PROD) exec -T db psql -U postgres smartlib < $(FILE)
	@echo "Production database restored from $(FILE)!"

# Registry Commands
push-registry:
	@if [ -z "$(REGISTRY_USER)" ] || [ -z "$(REGISTRY_REPO)" ]; then \
		echo "Usage: make push-registry REGISTRY_USER=username REGISTRY_REPO=repo"; exit 1; fi
	docker login
	docker tag smartlib_web $(REGISTRY_USER)/$(REGISTRY_REPO):latest
	docker push $(REGISTRY_USER)/$(REGISTRY_REPO):latest
	@echo "Image pushed to $(REGISTRY_USER)/$(REGISTRY_REPO):latest"

# Utility Commands
status:
	$(DOCKER_COMPOSE) ps

prod-status:
	$(DOCKER_COMPOSE_PROD) ps

stats:
	docker stats

restart:
	$(DOCKER_COMPOSE) restart

restart-web:
	$(DOCKER_COMPOSE) restart web

restart-nginx:
	$(DOCKER_COMPOSE) restart nginx

health-check:
	@curl -f http://localhost:8000/health/ && echo "✓ Application is healthy" || echo "✗ Application is not healthy"

# Setup Commands
init: build up migrate createsuperuser
	@echo "SmartLib Docker setup complete!"
	@echo "Access the application at http://localhost:8000"
	@echo "Admin panel at http://localhost:8000/admin"

prod-init: prod-build prod-up
	@echo "SmartLib Production setup complete!"
	@echo "Application is running on port 80"
