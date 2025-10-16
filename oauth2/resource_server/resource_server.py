"""
OAuth 2.0 Resource Server

This server protects resources and validates access tokens with the Authorization Server.
"""

from flask import Flask, request, jsonify
import os
from flask_cors import CORS
import logging
import requests

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [RESOURCE SERVER] %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Auth server configuration
AUTH_SERVER_HOST = os.getenv("AUTH_SERVER_HOST", os.getenv("HOST_IP", "localhost"))
AUTH_SERVER_URL = "http://{}:5050".format(AUTH_SERVER_HOST)

# Sample protected data
PROTECTED_DATA = {
    "user1": {
        "name": "John Doe",
        "email": "john@example.com",
        "subscription": "premium"
    },
    "user2": {
        "name": "Jane Smith",
        "email": "jane@example.com",
        "subscription": "basic"
    }
}

def validate_token(access_token):
    """
    Validate the access token with the Authorization Server
    Returns (is_valid, error_message)
    """
    try:
        response = requests.post(
            f"{AUTH_SERVER_URL}/validate",
            json={"access_token": access_token},
            timeout=5
        )
        
        if response.status_code == 200:
            return True, None
        else:
            error_data = response.json()
            return False, error_data.get("error", "Token validation failed")
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Error communicating with auth server: {str(e)}")
        return False, "Error validating token with authorization server"

@app.route('/')
def index():
    return "OAuth 2.0 Resource Server - Running!"

@app.route('/api/user-data')
def get_user_data():
    """Protected endpoint that requires a valid access token"""
    logger.info("Received request for protected user data")
    
    # Get the authorization header
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        logger.error("No valid authorization header found")
        return jsonify({"error": "Missing or invalid authorization header"}), 401

    # Extract the token
    access_token = auth_header.split(' ')[1]
    logger.info(f"Received access token: {access_token}")
    
    # Validate the token with the Authorization Server
    is_valid, error = validate_token(access_token)
    
    if not is_valid:
        logger.error(f"Token validation failed: {error}")
        return jsonify({"error": error}), 401
    
    # If we get here, the token is valid
    logger.info("Token is valid, returning protected data")
    return jsonify({
        "message": "Access granted!",
        "data": PROTECTED_DATA
    })

if __name__ == '__main__':
    logger.info("Starting OAuth 2.0 Resource Server on port 5051")
    app.run(host='0.0.0.0', port=5051, debug=True)
