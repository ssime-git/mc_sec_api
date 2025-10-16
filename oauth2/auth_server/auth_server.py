"""
OAuth 2.0 Authorization Server

This server implements the OAuth 2.0 authorization flow:
1. Client requests authorization (/authorize endpoint)
2. Server validates client and generates auth code
3. Client exchanges auth code for access token (/token endpoint)

Key Concepts:
- Client ID: Identifies the application requesting access
- Client Secret: Secret key to authenticate the application
- Authorization Code: Short-lived code used to obtain access token
- Access Token: Token used to access protected resources
"""

from flask import Flask, request, jsonify, redirect
import os
import random
import string
import time
import logging

# Set up logging to show what's happening
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [AUTH SERVER] %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# In a real application, these would be stored in a secure database
clients = {
    "myclient": {
        "client_secret": "mysecret",
        "redirect_uri": "http://{}:5052/callback".format(os.getenv("HOST_IP", "localhost"))
    }
}
auth_codes = {}  # Store auth codes temporarily
tokens = {}      # Store access tokens

@app.route('/')
def index():
    return "OAuth 2.0 Authorization Server - Running!"

@app.route('/authorize')
def authorize():
    """
    Step 1 of OAuth 2.0: Authorization Request
    
    The client redirects the user here with these parameters:
    - client_id: Identifies the client application
    - redirect_uri: Where to send the authorization code
    """
    logger.info("=== Step 1: Authorization Request ===")
    
    # 1. Get and validate client details
    client_id = request.args.get('client_id')
    redirect_uri = request.args.get('redirect_uri')
    
    logger.info(f"Received authorization request from client_id: {client_id}")
    logger.info(f"Redirect URI: {redirect_uri}")
    
    # 2. Validate the client
    if client_id not in clients:
        logger.error(f"Invalid client_id: {client_id}")
        return "Invalid client", 400
        
    if redirect_uri != clients[client_id]['redirect_uri']:
        logger.error(f"Invalid redirect_uri: {redirect_uri}")
        return "Invalid redirect URI", 400
    
    # 3. Generate authorization code
    auth_code = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    auth_codes[auth_code] = {
        'client_id': client_id,
        'expires': time.time() + 600  # 10 minutes expiration
    }
    
    logger.info(f"Generated authorization code: {auth_code}")
    logger.info("Redirecting user back to client application...")
    
    # 4. Redirect back to client with auth code
    return redirect(f"{redirect_uri}?code={auth_code}")

@app.route('/token', methods=['POST'])
def token():
    """
    Step 2 of OAuth 2.0: Token Request
    
    The client sends:
    - client_id: Identifies the client application
    - client_secret: Proves the client's identity
    - auth_code: The code received from /authorize
    """
    logger.info("=== Step 2: Token Request ===")
    
    try:
        data = request.json
        auth_code = data.get('auth_code')
        client_id = data.get('client_id')
        client_secret = data.get('client_secret')
        
        logger.info(f"Client {client_id} requesting access token with auth code: {auth_code}")
        
        # 1. Validate the authorization code
        if not auth_code or auth_code not in auth_codes:
            logger.error("Invalid authorization code")
            return jsonify({"error": "Invalid authorization code"}), 400
            
        # 2. Check if auth code has expired
        code_data = auth_codes[auth_code]
        if time.time() > code_data['expires']:
            logger.error("Authorization code has expired")
            return jsonify({"error": "Authorization code expired"}), 400
            
        # 3. Validate client credentials
        if (code_data['client_id'] != client_id or 
            clients[client_id]['client_secret'] != client_secret):
            logger.error("Invalid client credentials")
            return jsonify({"error": "Invalid client credentials"}), 400
        
        # 4. Generate access token
        access_token = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
        tokens[access_token] = {
            'client_id': client_id,
            'expires': time.time() + 3600  # 1 hour expiration
        }
        
        # 5. Remove used auth code
        del auth_codes[auth_code]
        
        logger.info(f"Generated access token: {access_token}")
        logger.info("Token exchange successful!")
        
        return jsonify({"access_token": access_token})
        
    except Exception as e:
        logger.error(f"Error during token exchange: {str(e)}")
        return jsonify({"error": "Server error"}), 500

@app.route('/validate', methods=['POST'])
def validate_token():
    """
    Token validation endpoint
    
    Resource servers call this endpoint to validate access tokens
    Returns token information if valid, error if not
    """
    logger.info("=== Token Validation Request ===")
    
    try:
        data = request.json
        access_token = data.get('access_token')
        
        logger.info(f"Validating access token: {access_token}")
        
        # Check if token exists
        if not access_token or access_token not in tokens:
            logger.error("Invalid access token")
            return jsonify({"valid": False, "error": "Invalid token"}), 401
            
        # Check if token has expired
        token_data = tokens[access_token]
        if time.time() > token_data['expires']:
            logger.error("Token has expired")
            # Remove expired token
            del tokens[access_token]
            return jsonify({"valid": False, "error": "Token expired"}), 401
        
        logger.info("Token is valid!")
        return jsonify({
            "valid": True,
            "client_id": token_data['client_id'],
            "expires": token_data['expires']
        })
        
    except Exception as e:
        logger.error(f"Error during token validation: {str(e)}")
        return jsonify({"valid": False, "error": "Server error"}), 500

if __name__ == '__main__':
    logger.info("Starting OAuth 2.0 Authorization Server on port 5050")
    app.run(host='0.0.0.0', port=5050, debug=True)
