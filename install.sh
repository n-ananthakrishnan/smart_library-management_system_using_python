#!/bin/bash

# SmartLib Docker Installation Script
# This script automates the Docker setup process

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
print_header() {
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}$1${NC}"
    echo -e "${GREEN}========================================${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

check_requirements() {
    print_header "Checking Requirements"
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed!"
        echo "Please install Docker from: https://www.docker.com/products/docker-desktop"
        exit 1
    fi
    print_success "Docker installed: $(docker --version)"
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed!"
        echo "Please install Docker Compose or use Docker CLI v2.0+"
        exit 1
    fi
    print_success "Docker Compose installed: $(docker-compose --version)"
    
    # Check Docker daemon
    if ! docker ps &> /dev/null; then
        print_error "Docker daemon is not running!"
        echo "Please start Docker Desktop or Docker daemon"
        exit 1
    fi
    print_success "Docker daemon is running"
}

setup_environment() {
    print_header "Setting Up Environment"
    
    if [ -f .env ]; then
        print_warning ".env file already exists, skipping..."
    else
        if [ ! -f .env.example ]; then
            print_error ".env.example not found!"
            exit 1
        fi
        cp .env.example .env
        print_success "Created .env from template"
        
        read -p "Do you want to edit .env now? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            ${EDITOR:-nano} .env
        fi
    fi
}

build_images() {
    print_header "Building Docker Images"
    
    print_warning "This may take a few minutes..."
    docker-compose build --no-cache
    print_success "Docker images built successfully"
}

start_services() {
    print_header "Starting Services"
    
    docker-compose up -d
    
    # Wait for services to be healthy
    print_warning "Waiting for services to be ready (this may take 30 seconds)..."
    
    sleep 5
    
    local max_attempts=30
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if docker-compose exec -T web curl -f http://localhost:8000/health/ &> /dev/null; then
            print_success "Application is healthy"
            break
        fi
        attempt=$((attempt + 1))
        if [ $attempt -eq $max_attempts ]; then
            print_warning "Application is still starting, please wait..."
        fi
        sleep 1
    done
}

run_migrations() {
    print_header "Running Migrations"
    
    docker-compose exec web python manage.py migrate --noinput
    print_success "Migrations completed"
}

collect_static() {
    print_header "Collecting Static Files"
    
    docker-compose exec web python manage.py collectstatic --noinput
    print_success "Static files collected"
}

create_superuser() {
    print_header "Creating Superuser"
    
    echo "Enter superuser details:"
    read -p "Username (default: admin): " username
    username=${username:-admin}
    
    read -p "Email (default: admin@smartlib.local): " email
    email=${email:-admin@smartlib.local}
    
    read -sp "Password: " password
    echo
    
    if [ -z "$password" ]; then
        print_warning "Using default password: admin123"
        password="admin123"
    fi
    
    docker-compose exec -T web python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if User.objects.filter(username='$username').exists():
    print(f"User '$username' already exists!")
else:
    User.objects.create_superuser('$username', '$email', '$password')
    print(f"Superuser '$username' created successfully!")
EOF
    
    print_success "Superuser created"
}

verify_installation() {
    print_header "Verifying Installation"
    
    echo ""
    docker-compose ps
    echo ""
    
    # Check if all services are running
    local status=$(docker-compose ps --quiet | wc -l)
    if [ $status -ge 4 ]; then
        print_success "All services are running"
    else
        print_warning "Some services may still be starting"
    fi
}

print_next_steps() {
    print_header "Installation Complete!"
    
    echo ""
    echo -e "${GREEN}Your SmartLib application is ready!${NC}"
    echo ""
    echo "Access the application at:"
    echo -e "  ${YELLOW}Web Interface:${NC} http://localhost:8000"
    echo -e "  ${YELLOW}Admin Panel:${NC} http://localhost:8000/admin"
    echo -e "  ${YELLOW}API:${NC} http://localhost:8000/api/"
    echo ""
    echo "Useful commands:"
    echo "  ${YELLOW}View logs:${NC}          docker-compose logs -f"
    echo "  ${YELLOW}Run shell:${NC}          docker-compose exec web python manage.py shell"
    echo "  ${YELLOW}Stop services:${NC}      docker-compose down"
    echo "  ${YELLOW}Help:${NC}              make help"
    echo ""
    echo "For more information, see:"
    echo "  - DOCKER_QUICKSTART.md"
    echo "  - DOCKER.md"
    echo ""
    echo -e "${GREEN}Happy coding! 🚀${NC}"
    echo ""
}

# Main script
main() {
    clear
    print_header "SmartLib Docker Installation"
    echo ""
    
    check_requirements
    echo ""
    
    setup_environment
    echo ""
    
    read -p "Install and start services? (y/n) " -n 1 -r
    echo
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_warning "Installation cancelled"
        exit 0
    fi
    
    build_images
    echo ""
    
    start_services
    echo ""
    
    run_migrations
    echo ""
    
    collect_static
    echo ""
    
    read -p "Create superuser now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        create_superuser
        echo ""
    fi
    
    verify_installation
    echo ""
    
    print_next_steps
}

# Run main function
main
