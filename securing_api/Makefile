# GDPR-Compliant API System Makefile

.PHONY: up down restart logs test register token pseudonymize user-data clean backup-db restore-db check-retention grant-consent get-consents db-list-users db-list-consents db-list-audit db-schema db-query db-count db-cleanup-expired db-check-expired streamlit-run streamlit-install streamlit-build

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

# Grant consent (requires TOKEN env var)
grant-consent:
	curl -X POST "http://localhost:8000/consent?consent_type=data_processing&granted=true&expires_days=30" \
		-H "Authorization: Bearer $${TOKEN}"

# Get user consents (requires TOKEN env var)
get-consents:
	curl -X GET "http://localhost:8000/consents" \
		-H "Authorization: Bearer $${TOKEN}"

# Check data retention logs
check-retention:
	docker compose logs security_api | grep "data_cleanup"

# Force data retention cleanup (for testing)
force-cleanup:
	docker compose restart security_api && \
	sleep 2 && \
	docker compose logs --tail 20 security_api | grep scheduler

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

# Database audit commands

# List all users in the database
db-list-users:
	docker exec security_api python -c "import sqlite3; conn = sqlite3.connect('/app/data/gdpr_db.sqlite'); cursor = conn.cursor(); cursor.execute('SELECT id, username, created_at FROM users'); rows = cursor.fetchall(); print('ID | USERNAME | CREATED_AT'); print('-' * 50); [print(f'{row[0]} | {row[1]} | {row[2]}') for row in rows]; conn.close()"

# List all consents in the database
db-list-consents:
	docker exec security_api python -c "import sqlite3; conn = sqlite3.connect('/app/data/gdpr_db.sqlite'); cursor = conn.cursor(); cursor.execute('SELECT username, consent_type, granted, granted_at, expires_at FROM consents'); rows = cursor.fetchall(); print('USERNAME | CONSENT_TYPE | GRANTED | GRANTED_AT | EXPIRES_AT'); print('-' * 80); [print(f'{row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[4]}') for row in rows]; conn.close()"

# List all audit log entries
db-list-audit:
	docker exec security_api python -c "import sqlite3; conn = sqlite3.connect('/app/data/gdpr_db.sqlite'); cursor = conn.cursor(); cursor.execute('SELECT timestamp, action_type, username, details FROM audit_log ORDER BY timestamp DESC LIMIT 20'); rows = cursor.fetchall(); print('TIMESTAMP | ACTION_TYPE | USERNAME | DETAILS'); print('-' * 80); [print(f'{row[0]} | {row[1]} | {row[2] or "None"} | {row[3] or "None"}') for row in rows]; conn.close()"

# Show database schema
db-schema:
	docker exec security_api python -c "import sqlite3; conn = sqlite3.connect('/app/data/gdpr_db.sqlite'); cursor = conn.cursor(); cursor.execute('SELECT sql FROM sqlite_master WHERE type=\'table\' ORDER BY name'); tables = cursor.fetchall(); [print(f'\n{table[0]}\n') for table in tables]; conn.close()"

# Run custom SQL query on the database
# Usage: make db-query SQL="SELECT * FROM users;"
db-query:
	docker exec security_api python -c "import sqlite3, sys; conn = sqlite3.connect('/app/data/gdpr_db.sqlite'); cursor = conn.cursor(); cursor.execute('${SQL}'); rows = cursor.fetchall(); [print(row) for row in rows]; conn.close()"

# Count records in each table
db-count:
	docker exec security_api python -c "import sqlite3; conn = sqlite3.connect('/app/data/gdpr_db.sqlite'); cursor = conn.cursor(); cursor.execute('SELECT COUNT(*) FROM users'); print(f'Users: {cursor.fetchone()[0]}'); cursor.execute('SELECT COUNT(*) FROM consents'); print(f'Consents: {cursor.fetchone()[0]}'); cursor.execute('SELECT COUNT(*) FROM audit_log'); print(f'Audit logs: {cursor.fetchone()[0]}'); conn.close()"

# Force cleanup of expired consents
db-cleanup-expired:
	docker exec security_api python -c "import sqlite3; conn = sqlite3.connect('/app/data/gdpr_db.sqlite'); cursor = conn.cursor(); cursor.execute('DELETE FROM consents WHERE expires_at < CURRENT_TIMESTAMP'); deleted = cursor.rowcount; print(f'Expired consents removed: {deleted}'); cursor.execute('INSERT INTO audit_log (action_type, details) VALUES (\'data_cleanup\', \'Manual cleanup of expired consents\')'); conn.commit(); conn.close(); print('Cleanup completed and logged')"

# Check for expired consents
db-check-expired:
	docker exec security_api python -c "import sqlite3; conn = sqlite3.connect('/app/data/gdpr_db.sqlite'); cursor = conn.cursor(); cursor.execute('SELECT username, consent_type, expires_at FROM consents WHERE expires_at < CURRENT_TIMESTAMP'); rows = cursor.fetchall(); print('Expired consents:'); [print(f'User: {row[0]}, Consent: {row[1]}, Expired: {row[2]}') for row in rows] if rows else print('No expired consents found'); conn.close()"

# Streamlit app commands

# Install Streamlit dependencies locally
streamlit-install:
	cd src/streamlit_app && pip install -r requirements.txt

# Run Streamlit app locally
streamlit-run:
	cd src/streamlit_app && streamlit run app.py

# Build and run Streamlit app with Docker
streamlit-build:
	docker compose build streamlit_app

# Open Streamlit app in browser
streamlit-open:
	open http://localhost:8502