.PHONY: install run-auth run-resource run-demo clean docker-build docker-up docker-down docker-logs docker-clean docker-restart help

# Local Development Commands
# ===========================

install:
	pip install -r requirements.txt

run-auth:
	python auth_server/auth_server.py

run-resource:
	python resource_server/resource_server.py

run:
	python run_demo.py

clean:
	find . -type d -name "__pycache__" -exec rm -r {} +

# Docker Commands
# ===============

docker-build:
	@echo "Building Docker images..."
	docker-compose build

docker-up:
	@echo "Starting OAuth2 demo services..."
	docker-compose up -d
	@echo ""
	@echo "Services are starting up. Access them at:"
	@echo "  Client App:      http://localhost:5052"
	@echo "  Auth Server:     http://localhost:5050"
	@echo "  Resource Server: http://localhost:5051"
	@echo ""
	@echo "Run 'make docker-logs' to view logs"

docker-down:
	@echo "Stopping OAuth2 demo services..."
	docker-compose down

docker-logs:
	@echo "Following logs from all services (Ctrl+C to exit)..."
	docker-compose logs -f

docker-clean:
	@echo "Removing containers, networks, and images..."
	docker-compose down -v --rmi all
	@echo "Cleanup complete!"

docker-restart:
	@echo "Restarting OAuth2 demo services..."
	docker-compose restart

docker-status:
	@echo "Service status:"
	docker-compose ps

docker-rebuild:
	@echo "Rebuilding and restarting services..."
	docker-compose down
	docker-compose build --no-cache
	docker-compose up -d
	@echo "Services rebuilt and started!"

# Help
# ====

help:
	@echo "OAuth2 Demo Makefile Commands"
	@echo "=============================="
	@echo ""
	@echo "Local Development:"
	@echo "  make install        - Install Python dependencies"
	@echo "  make run           - Run all services locally"
	@echo "  make run-auth      - Run only auth server"
	@echo "  make run-resource  - Run only resource server"
	@echo "  make clean         - Clean Python cache files"
	@echo ""
	@echo "Docker Commands:"
	@echo "  make docker-build    - Build Docker images"
	@echo "  make docker-up       - Start services in Docker"
	@echo "  make docker-down     - Stop Docker services"
	@echo "  make docker-logs     - View service logs"
	@echo "  make docker-restart  - Restart services"
	@echo "  make docker-rebuild  - Rebuild from scratch"
	@echo "  make docker-status   - Show service status"
	@echo "  make docker-clean    - Remove all containers and images"
	@echo ""
	@echo "Quick Start:"
	@echo "  1. make docker-build"
	@echo "  2. make docker-up"
	@echo "  3. Open http://localhost:5052 in browser"