import sqlite3
from passlib.context import CryptContext
from typing import Optional, Dict, List
import os
from datetime import datetime, timedelta

# Database setup
# Use absolute path for Docker volume mount compatibility
DB_PATH = "/app/users/gdpr_db.sqlite"
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_db_connection():
    """Get a database connection with foreign key support"""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    return conn

def init_db():
    """Initialize the database with all required tables"""
    conn = get_db_connection()
    try:
        # Users table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                hashed_password TEXT NOT NULL,
                disabled BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Consents table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS consents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                consent_type TEXT NOT NULL,
                granted BOOLEAN NOT NULL DEFAULT FALSE,
                granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                FOREIGN KEY (username) REFERENCES users(username) ON DELETE CASCADE,
                UNIQUE(username, consent_type)
            )
        """)
        
        # Audit log table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                action_type TEXT NOT NULL,
                username TEXT,
                details TEXT,
                FOREIGN KEY (username) REFERENCES users(username) ON DELETE SET NULL
            )
        """)
        
        conn.commit()
    finally:
        conn.close()

def register_user(username: str, password: str) -> bool:
    """Register a new user"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, hashed_password) VALUES (?, ?)",
            (username, pwd_context.hash(password))
        )
        
        # Log the registration
        cursor.execute(
            "INSERT INTO audit_log (action_type, username, details) VALUES (?, ?, ?)",
            ("user_registered", username, "User registration")
        )
        
        conn.commit()
        return True
    except sqlite3.IntegrityError:  # Username exists
        return False
    finally:
        conn.close()

def get_user(username: str) -> Optional[Dict]:
    """Get user by username"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT username, hashed_password, disabled FROM users WHERE username = ?",
            (username,)
        )
        row = cursor.fetchone()
        
        if row:
            return dict(row)  # Convert to regular dictionary
        return None
    finally:
        conn.close()

def verify_user(username: str, password: str) -> bool:
    """Verify user credentials"""
    user = get_user(username)
    if not user:
        return False
    return pwd_context.verify(password, user["hashed_password"])

def add_consent(username: str, consent_type: str, granted: bool = True, days_valid: int = 365) -> bool:
    """Add or update a consent record"""
    conn = get_db_connection()
    try:
        expires_at = (datetime.now() + timedelta(days=days_valid)).isoformat()
        conn.execute(
            """
            INSERT INTO consents (username, consent_type, granted, granted_at, expires_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(username, consent_type) DO UPDATE SET
                granted = ?,
                granted_at = CURRENT_TIMESTAMP,
                expires_at = ?
            """,
            (username, consent_type, granted, datetime.now().isoformat(), expires_at, 
             granted, expires_at)
        )
        
        # Log the consent action
        action = "consent_granted" if granted else "consent_revoked"
        conn.execute(
            "INSERT INTO audit_log (action_type, username, details) VALUES (?, ?, ?)",
            (action, username, f"Consent: {consent_type}")
        )
        
        conn.commit()
        return True
    except sqlite3.Error:
        return False
    finally:
        conn.close()

def get_user_consents(username: str) -> Dict[str, bool]:
    """Get all consents for a user"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT consent_type, granted FROM consents 
               WHERE username = ? AND expires_at > CURRENT_TIMESTAMP""",
            (username,)
        )
        return {row["consent_type"]: bool(row["granted"]) for row in cursor.fetchall()}
    finally:
        conn.close()

def validate_consents(username: str, required_consents: List[str]) -> bool:
    """Check if user has all required consents"""
    user_consents = get_user_consents(username)
    return all(user_consents.get(consent, False) for consent in required_consents)

def log_action(action_type: str, username: str = None, details: str = None) -> bool:
    """Log a GDPR-relevant action"""
    conn = get_db_connection()
    try:
        conn.execute(
            "INSERT INTO audit_log (action_type, username, details) VALUES (?, ?, ?)",
            (action_type, username, details)
        )
        conn.commit()
        return True
    except sqlite3.Error:
        return False
    finally:
        conn.close()

def cleanup_expired_data():
    """Remove expired consents and perform other cleanup tasks"""
    conn = get_db_connection()
    try:
        # Delete expired consents
        conn.execute("DELETE FROM consents WHERE expires_at < CURRENT_TIMESTAMP")
        
        # Log the cleanup action
        conn.execute(
            "INSERT INTO audit_log (action_type, details) VALUES (?, ?)",
            ("data_cleanup", "Removed expired consents")
        )
        
        conn.commit()
    finally:
        conn.close()
