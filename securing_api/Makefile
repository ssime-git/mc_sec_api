# GDPR-Compliant API System Makefile

.PHONY: up down restart logs test register token pseudonymize user-data clean backup-db restore-db

# Start services
up:
	docker compose up --build -d

# Stop services
down:
	docker compose down

# Restart services
restart: down up

# View logs
logs:
	docker compose logs -f

# Run all tests
test:
	./test_api.sh

# Register a new user
register:
	curl -X POST "http://localhost:8000/register" \
		-H "Content-Type: application/json" \
		-d '{"username":"testuser","password":"Testpass123!"}'

# Get authentication token
token:
	curl -X POST "http://localhost:8000/token" \
		-H "Content-Type: application/x-www-form-urlencoded" \
		-d "username=testuser&password=Testpass123!"

# Pseudonymize data (requires TOKEN env var)
pseudonymize:
	curl -X POST "http://localhost:8000/pseudonymize" \
		-H "Authorization: Bearer $${TOKEN}" \
		-H "Content-Type: application/json" \
		-d '{"name":"John Doe","email":"john@example.com"}'



# Zodiac sign prediction (requires TOKEN env var)
predict-zodiac:
	curl -X POST "http://localhost:8000/forward-to-prediction" \
		-H "Authorization: Bearer $${TOKEN}" \
		-H "Content-Type: application/json" \
		-d '{"age":30,"sex":"Male","favorite_color":"Blue","favorite_food":"Pizza"}'

# Get user data (requires TOKEN env var)
user-data:
	curl -X GET "http://localhost:8000/user/data" \
		-H "Authorization: Bearer $${TOKEN}"

# Clean temporary files
clean:
	find . -name "__pycache__" -type d -exec rm -rf {} +
	find . -name "*.pyc" -delete

# Backup database
backup-db:
	mkdir -p backups
	tar -czf backups/users-$$(date +%Y%m%d-%H%M%S).tar.gz users/

# Restore database from latest backup
restore-db:
	latest=$$(ls -t backups/users-*.tar.gz | head -1) && \
	if [ -n "$$latest" ]; then \
		tar -xzf $$latest; \
		echo "Restored from $$latest"; \
	else \
		echo "No backups found"; \
	fi