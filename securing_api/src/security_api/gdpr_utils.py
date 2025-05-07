import hashlib
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

# Import from unified database module
from user_db import log_action as db_log_action

class GDPRUtils:
    def __init__(self, retention_days: int = 30, log_file: str = "/app/logs/gdpr_audit.log"):
        self.retention_days = retention_days
        self.log_file = log_file
        self.setup_logging()
        
    def setup_logging(self):
        """Set up logging for GDPR-related actions"""
        self.logger = logging.getLogger("gdpr_logger")
        self.logger.setLevel(logging.INFO)
        
        # Create logs directory if it doesn't exist
        log_dir = os.path.dirname(self.log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        handler = logging.FileHandler(self.log_file)
        formatter = logging.Formatter('%(asctime)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
    
    def log_action(self, action_type: str, user_id: str, details: str = ""):
        """Log a GDPR-related action"""
        # Log to file
        log_message = f"{action_type.upper()} - User: {user_id} - Details: {details}"
        self.logger.info(log_message)
        
        # Also log to database
        db_log_action(action_type, user_id, details)
    
    def pseudonymize_data(self, data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Pseudonymize personal data"""
        result = {}
        for key, value in data.items():
            if isinstance(value, str) and self._is_personal_data(key):
                # Simple pseudonymization by using a prefix and user_id
                result[key] = f"pseudo_{user_id}_{key}"
            else:
                result[key] = value
        return result
    
    def _is_personal_data(self, field_name: str) -> bool:
        """Check if a field might contain personal data"""
        personal_fields = [
            "name", "email", "phone", "address", "location", "birth", 
            "ssn", "social", "passport", "license", "id", "zip", "postal",
            "city", "country", "street", "gender", "age", "dob", "date_of_birth"
        ]
        return any(personal in field_name.lower() for personal in personal_fields)
    
    def check_retention_period(self, timestamp: datetime) -> bool:
        """Check if data is within retention period"""
        retention_limit = datetime.now() - timedelta(days=self.retention_days)
        return timestamp > retention_limit
    
    def schedule_data_cleanup(self, scheduler):
        """Schedule regular data cleanup"""
        scheduler.add_job(
            self._cleanup_expired_data,
            'interval',
            days=1,
            id='data_cleanup',
            replace_existing=True
        )
    
    def _cleanup_expired_data(self):
        """Clean up expired data"""
        # This would connect to your database and remove expired data
        from .user_db import cleanup_expired_data
        cleanup_expired_data()
        self.log_action("data_cleanup", None, f"Removed data older than {self.retention_days} days")
