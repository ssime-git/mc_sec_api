# GDPR-Compliant API System

## Architecture Overview

This project implements a GDPR-compliant machine learning API system using a two-API architecture that separates security concerns from prediction functionality. This separation is crucial for maintaining GDPR compliance while allowing the ML system to operate efficiently.

```txt
┌─────────────────┐         ┌─────────────────┐
│                 │         │                 │
│    Client       │         │   Admin/User    │
│    Application  │         │   Interface     │
│                 │         │                 │
└────────┬────────┘         └────────┬────────┘
         │                           │
         │                           │
         │                           │
         ▼                           ▼
┌─────────────────────────────────────────────┐
│                                             │
│            Security/GDPR API                │
│                                             │
│  ┌─────────────┐  ┌────────────────────┐   │
│  │ Auth & JWT  │  │ Consent Management │   │
│  └─────────────┘  └────────────────────┘   │
│                                             │
│  ┌─────────────┐  ┌────────────────────┐   │
│  │ User Data   │  │ Pseudonymization   │   │
│  └─────────────┘  └────────────────────┘   │
│                                             │
└──────────────────────┬──────────────────────┘
                       │
                       │ Internal API Key
                       │ Pseudonymized Data
                       ▼
┌─────────────────────────────────────────────┐
│                                             │
│              Prediction API                 │
│                                             │
│  ┌─────────────┐  ┌────────────────────┐   │
│  │ ML Model    │  │ Feature Processing │   │
│  └─────────────┘  └────────────────────┘   │
│                                             │
│  ┌─────────────────────────────────────┐   │
│  │ No Access to Personal Identifiers   │   │
│  └─────────────────────────────────────┘   │
│                                             │
└─────────────────────────────────────────────┘
```

### Why This Architecture?

1. **Separation of Concerns**
   - Security API handles all PII (Personally Identifiable Information) and GDPR compliance
   - Prediction API works only with pseudonymized data, reducing compliance scope

2. **Data Protection by Design**
   - PII never reaches the prediction system
   - Consent tracking happens before data processing
   - Audit logging captures all GDPR-relevant actions

3. **Scalability**
   - Each API can scale independently based on different workloads
   - ML models can be updated without affecting security components

## Implementation Details

### Core Components

1. **Security/GDPR API** (Port 8000)
   - **Authentication**: JWT-based token system with bcrypt password hashing
   - **User Management**: SQLite database with secure storage
   - **Consent Tracking**: Explicit consent required for data processing
   - **Data Pseudonymization**: Transforms PII into non-identifiable format
   - **GDPR Rights**: Endpoints for data access, deletion, and consent management

2. **Prediction API** (Port 8001)
   - **Internal Authentication**: API key validation
   - **ML Model**: Scikit-learn based prediction system
   - **Data Processing**: Works only with pseudonymized features
   - **No PII Access**: Cannot reverse pseudonymization

### API Communication Flow

1. Client authenticates with Security API and receives JWT token
2. Client sends data with token to Security API
3. Security API:
   - Validates token and consent
   - Pseudonymizes sensitive data
   - Forwards request to Prediction API with internal API key
4. Prediction API:
   - Validates internal API key
   - Makes prediction on pseudonymized data
   - Returns results to Security API
5. Security API returns results to client

## Setup & Installation

```bash
# Clone repository and navigate to project directory
cd securing_api

# Start services
docker compose up --build

# Or use the Makefile
make up
```

## API Endpoints

### Security API
- `POST /register` - Register new user
- `POST /token` - Get JWT authentication token
- `POST /pseudonymize` - Pseudonymize sensitive data
- `POST /consent` - Manage user consent preferences
- `GET /user/data` - Access user data (GDPR right of access)
- `DELETE /user/data` - Delete user data (GDPR right to erasure)
- `POST /forward-to-prediction` - Forward pseudonymized data to Prediction API

### Prediction API
- `POST /predict` - Make predictions (internal use only)

## Testing

Use the provided test script to verify functionality:

```bash
./test_api.sh
```

Or test individual endpoints:

```bash
# Register user
curl -X POST "http://localhost:8000/register" \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"Testpass123!"}'

# Get token
curl -X POST "http://localhost:8000/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=Testpass123!"

# Store token for subsequent requests
TOKEN="your-token-here"

# Make prediction with pseudonymized data
curl -X POST "http://localhost:8000/forward-to-prediction" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"feature1":1,"feature2":2,"feature3":3}'
```

## GDPR Compliance Features

- **Data Pseudonymization**: PII is transformed before processing
- **Consent Management**: Explicit opt-in required for data processing
- **Audit Logging**: All GDPR-relevant actions are logged
- **Data Retention**: 30-day automatic cleanup of expired data
- **Right to Access**: Endpoints for users to access their data
- **Right to Erasure**: Endpoints for users to delete their data

## Database Architecture

The system uses a unified SQLite database stored in the `data/` directory, which is mounted as a volume for persistence across container restarts. This approach ensures data consistency, enables proper foreign key relationships, and simplifies backup and maintenance.

### Database Structure

1. **Unified Database** (`gdpr_db.sqlite`)
   
   - **Table: users**
     - `id`: Integer, Primary Key, Autoincrement
     - `username`: Text, Unique
     - `hashed_password`: Text (bcrypt hashed)
     - `disabled`: Boolean
     - `created_at`: Timestamp
   
   - **Table: consents**
     - `id`: Integer, Primary Key, Autoincrement
     - `username`: Text (Foreign key to users.username)
     - `consent_type`: Text (e.g., "data_processing", "data_storage")
     - `granted`: Boolean
     - `granted_at`: Timestamp
     - `expires_at`: Timestamp
     - Foreign Key: username references users(username) ON DELETE CASCADE
     - Unique Constraint: (username, consent_type)
   
   - **Table: audit_log**
     - `id`: Integer, Primary Key, Autoincrement
     - `timestamp`: Timestamp
     - `action_type`: Text
     - `username`: Text (Foreign key to users.username)
     - `details`: Text
     - Foreign Key: username references users(username) ON DELETE SET NULL

2. **External Audit Log** (`/app/logs/gdpr_audit.log`)
   - Redundant log file for compliance and debugging
   - Format: `[timestamp] action_type - User: username - Details: additional_info`
   - Actions logged: user_registered, user_login, data_access, pseudonymization, etc.

### Data Lifecycle

1. **User Registration**
   - User credentials stored in users.db
   - Default consents created in consents.db
   - Registration logged in audit log

2. **Authentication**
   - Credentials verified against users.db
   - Consents checked in consents.db
   - Login logged in audit log

3. **Data Processing**
   - PII pseudonymized before processing
   - Only pseudonymized data sent to Prediction API
   - Processing logged in audit log

4. **Data Retention**
   - Background scheduler runs cleanup of expired data
   - Consents with passed expiration dates are removed
   - Cleanup actions logged in audit log

## Project Structure

```sh
securing_api/
├── src/
│   ├── security_api/        # GDPR compliance and security
│   │   ├── security_api.py  # Main API endpoints
│   │   ├── consent_manager.py # Consent tracking
│   │   ├── gdpr_utils.py    # Pseudonymization and logging
│   │   ├── user_db.py       # Unified database management
│   │   └── requirements.txt # Dependencies
│   └── prediction_api/      # ML prediction service
│       ├── prediction_api.py # Prediction endpoints
│       └── requirements.txt # Dependencies
├── docker/                  # Docker configuration
│   ├── Dockerfile.security  # Security API container
│   └── Dockerfile.prediction # Prediction API container
├── data/                    # Persistent database storage
│   └── gdpr_db.sqlite       # Unified SQLite database
├── logs/                    # GDPR audit logs
│   └── gdpr_audit.log       # Audit log file
├── models/                  # ML model storage
├── docker-compose.yml       # Service orchestration
├── Makefile                 # Common commands
└── test_api.sh              # Comprehensive testing script
```

## Implementation Improvements

### 1. Unified Database Architecture

We've implemented a single SQLite database with multiple tables instead of separate databases. This approach provides several benefits:

- **Data Consistency**: Foreign key constraints ensure referential integrity
- **Simplified Transactions**: Operations across tables can be atomic
- **Reduced Complexity**: One connection pool and consistent error handling
- **Better Performance**: Fewer file handles and connection overhead
- **Easier Backup**: Single file to back up and restore

### 2. Robust Persistence

The database is properly persisted through Docker volumes:

- **Named Volumes**: Clear separation between data and application code
- **Read-Write Permissions**: Explicit permission settings for security
- **Automatic Restart**: Containers restart automatically if they crash
- **Backup Mechanism**: Built-in commands for database backup/restore

### 3. Comprehensive Testing

The system includes a complete testing script that verifies:

- User registration and authentication
- Consent management
- Data pseudonymization
- Prediction functionality
- Error handling
- Database persistence
- GDPR compliance

## Development

Use the Makefile for common operations:

```bash
make up        # Start services
make down      # Stop services
make logs      # View logs
make test      # Run tests
make backup-db # Backup database
```
