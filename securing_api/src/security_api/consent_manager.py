from datetime import datetime
from typing import List
from pydantic import BaseModel
from typing import Optional

# Import from unified database module
from user_db import (
    add_consent,
    get_user_consents,
    validate_consents as db_validate_consents,
    log_action,
    cleanup_expired_data
)

class ConsentRecord(BaseModel):
    consent_type: str
    granted: bool
    timestamp: datetime
    expires: Optional[datetime] = None

class ConsentManager:
    def __init__(self, required_consents: List[str]):
        self.required_consents = required_consents

    def add_consent(
        self, 
        user_id: str, 
        consent_type: str, 
        granted: bool = True,
        days_valid: int = 365
    ) -> bool:
        """Add a consent record for a user"""
        # Use the unified database function
        result = add_consent(user_id, consent_type, granted, days_valid)
        return result

    def grant_consent(self, username: str, consent_type: str, days_valid: int = 365) -> bool:
        """Grant a specific consent"""
        # Use the unified database function
        return add_consent(username, consent_type, True, days_valid)

    def revoke_consent(self, user_id: str, consent_type: str) -> bool:
        """Revoke a specific consent"""
        # Use the unified database function
        return add_consent(user_id, consent_type, False, 0)  # Expired immediately

    def validate_consents(self, username: str) -> bool:
        """Check if user has all required consents"""
        # Use the unified database function
        return db_validate_consents(username, self.required_consents)

    def get_user_consents(self, username: str) -> dict:
        """Get all consents for a user"""
        # Use the unified database function
        return get_user_consents(username)

    def has_required_consents(self, username: str) -> bool:
        """Check if user has all required consents (alias for validate_consents)"""
        return self.validate_consents(username)

    def cleanup_expired_consents(self):
        """Clean up expired consents"""
        # Use the unified database function
        deleted_count = cleanup_expired_data()
        # Log the cleanup with count of deleted records
        log_action("consent_cleanup", None, f"Removed {deleted_count} expired consents")
        print(f"Data retention cleanup completed: {deleted_count} expired consents removed")
        return deleted_count
