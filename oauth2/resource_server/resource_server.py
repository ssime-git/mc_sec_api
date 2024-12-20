"""
OAuth 2.0 Resource Server

This server protects resources and validates access tokens with the Authorization Server.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [RESOURCE SERVER] %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

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
    
    # In a real application, we would validate the token with the Authorization Server
    # For this demo, we'll accept any token and return sample data
    try:
        # Simulate token validation
        if access_token:
            logger.info("Token is valid, returning protected data")
            return jsonify({
                "message": "Access granted!",
                "data": PROTECTED_DATA["user1"]  # Return sample data
            })
        else:
            logger.error("Invalid token")
            return jsonify({"error": "Invalid token"}), 401
            
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    logger.info("Starting OAuth 2.0 Resource Server on port 5051")
    app.run(port=5051, debug=True)
