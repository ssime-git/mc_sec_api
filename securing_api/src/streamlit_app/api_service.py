import requests
import os
import streamlit as st
from typing import Dict, List, Any, Optional

class APIService:
    """Service class for API interactions"""
    
    def __init__(self):
        self.security_api_url = os.environ.get("SECURITY_API_URL", "http://localhost:8000")
        self.prediction_api_url = os.environ.get("PREDICTION_API_URL", "http://localhost:8001")
    
    def get_auth_header(self) -> Dict[str, str]:
        """Get authentication header with token"""
        if 'token' not in st.session_state:
            return {}
        return {"Authorization": f"Bearer {st.session_state.token}"}
    
    def login(self, username: str, password: str) -> tuple[bool, str]:
        """Authenticate user with the security API"""
        try:
            print(f"Attempting login for user: {username}")
            print(f"Using API URL: {self.security_api_url}/token")
            
            response = requests.post(
                f"{self.security_api_url}/token",
                data={"username": username, "password": password},
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            print(f"Login response status code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                token = data.get("access_token")
                if token:
                    print("Login successful, token received")
                    return True, "Login successful"
                else:
                    print("Login failed: No token in response")
                    return False, "Authentication failed: No token received"
            else:
                try:
                    error_detail = response.json().get('detail', 'Unknown error')
                    print(f"Login failed: {error_detail}")
                except Exception:
                    error_detail = response.text or 'Unknown error'
                    print(f"Login failed with exception: {error_detail}")
                
                return False, f"Authentication failed: {error_detail}"
        except Exception as e:
            print(f"Login exception: {str(e)}")
            return False, f"Error connecting to authentication service: {str(e)}"
    
    def register(self, username: str, password: str) -> tuple[bool, str]:
        """Register a new user"""
        return self.register_user(username, password)
        
    def register_user(self, username: str, password: str) -> tuple[bool, str]:
        """Register a new user"""
        try:
            response = requests.post(
                f"{self.security_api_url}/register",
                json={"username": username, "password": password}
            )
            
            if response.status_code == 200:
                return True, "Registration successful"
            else:
                try:
                    error_detail = response.json().get('detail', 'Unknown error')
                except Exception:
                    error_detail = response.text or 'Unknown error'
                
                return False, error_detail
        except Exception as e:
            return False, str(e)
    
    def update_consent(self, consent_type: str, granted: bool, expiration_days: int) -> tuple[bool, str]:
        """Update user consent"""
        try:
            response = requests.post(
                f"{self.security_api_url}/consent",
                json={
                    "consent_type": consent_type,
                    "granted": granted,
                    "expiration_days": expiration_days
                },
                headers=self.get_auth_header()
            )
            
            if response.status_code == 200:
                return True, "Consent updated successfully"
            else:
                try:
                    error_detail = response.json().get('detail', 'Unknown error')
                except Exception:
                    error_detail = response.text or 'Unknown error'
                
                return False, error_detail
        except Exception as e:
            return False, str(e)
            
    def get_consents(self) -> List[Dict[str, Any]]:
        """Get user consents"""
        try:
            response = requests.get(
                f"{self.security_api_url}/consents",
                headers=self.get_auth_header()
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                try:
                    error_detail = response.json().get('detail', 'Unknown error')
                except Exception:
                    error_detail = response.text or 'Unknown error'
                
                return [{"error": error_detail}]
        except Exception as e:
            return [{"error": str(e)}]
    
    def update_consents(self, consent_types: List[str], expires_days: int) -> tuple[bool, str]:
        """Update user consents"""
        try:
            # First revoke all consents
            for consent_type in ["data_processing", "data_storage"]:
                success, message = self.update_consent(consent_type, False, 30)
                if not success:
                    return False, f"Error revoking consent: {message}"
            
            # Then grant selected consents
            for consent_type in consent_types:
                success, message = self.update_consent(consent_type, True, expires_days)
                if not success:
                    return False, f"Error granting consent: {message}"
            
            return True, "Consents updated successfully"
        except Exception as e:
            return False, str(e)
    
    def get_user_data(self) -> Dict[str, Any]:
        """Get user data"""
        try:
            response = requests.get(
                f"{self.security_api_url}/user/data",
                headers=self.get_auth_header()
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                error_detail = response.json().get('detail', 'Unknown error')
                return {"error": error_detail}
        except Exception as e:
            return {"error": str(e)}
    
    def make_prediction(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Make a prediction"""
        try:
            response = requests.post(
                f"{self.security_api_url}/forward-to-prediction",
                json=data,
                headers=self.get_auth_header()
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                error_detail = response.json().get('detail', 'Unknown error')
                return {"error": error_detail}
        except Exception as e:
            return {"error": str(e)}
    
    def run_db_command(self, command: str) -> List[Dict[str, Any]]:
        """Run a database command (admin only)"""
        try:
            # Debug information
            print(f"Attempting to run database command: {command}")
            print(f"Using API URL: {self.security_api_url}/admin/db-command")
            print(f"Auth headers present: {bool(self.get_auth_header())}")
            
            # Make the API request
            response = requests.get(
                f"{self.security_api_url}/admin/db-command",
                params={"command": command},
                headers=self.get_auth_header()
            )
            
            # Debug response
            print(f"Response status code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"Received successful response with {len(result)} items")
                return result
            else:
                try:
                    error_detail = response.json().get('detail', 'Unknown error')
                except Exception:
                    error_detail = response.text or 'Unknown error'
                print(f"Error response: {error_detail}")
                return [{"error": error_detail}]
        except Exception as e:
            print(f"Exception in run_db_command: {str(e)}")
            return [{"error": str(e)}]
    
    def test_connection(self) -> Dict[str, Any]:
        """Test connection to APIs"""
        results = {}
        
        # Test Security API
        try:
            response = requests.get(f"{self.security_api_url}/health")
            if response.status_code == 200:
                results["security_api"] = {
                    "status": "connected",
                    "details": response.json()
                }
            else:
                results["security_api"] = {
                    "status": "error",
                    "details": f"Status code: {response.status_code}"
                }
        except Exception as e:
            results["security_api"] = {
                "status": "error",
                "details": str(e)
            }
        
        # Test Prediction API
        try:
            response = requests.get(f"{self.prediction_api_url}/health")
            if response.status_code == 200:
                results["prediction_api"] = {
                    "status": "connected",
                    "details": response.json()
                }
            else:
                results["prediction_api"] = {
                    "status": "error",
                    "details": f"Status code: {response.status_code}"
                }
        except Exception as e:
            results["prediction_api"] = {
                "status": "error",
                "details": str(e)
            }
        
        return results
        
    def delete_account(self) -> tuple[bool, str]:
        """Delete user account"""
        try:
            response = requests.delete(
                f"{self.security_api_url}/user",
                headers=self.get_auth_header()
            )
            
            if response.status_code == 200:
                return True, "Account deleted successfully"
            else:
                try:
                    error_detail = response.json().get('detail', 'Unknown error')
                except Exception:
                    error_detail = response.text or 'Unknown error'
                
                return False, error_detail
        except Exception as e:
            return False, str(e)
