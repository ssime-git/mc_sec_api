"""
OAuth 2.0 Client Application

This application demonstrates the client-side of the OAuth 2.0 flow:
1. User clicks "Login" and is redirected to Authorization Server
2. After authorization, receives auth code via redirect
3. Exchanges auth code for access token
4. Uses access token to access protected resources

Flow Diagram:
User -> Client App -> Auth Server (authorize) -> Client App (with auth code)
Client App -> Auth Server (exchange token) -> Client App (with access token)
"""

from flask import Flask, request, redirect, render_template, session
import requests
import secrets
import logging

# Set up logging to show what's happening
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [CLIENT APP] %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # Required for session management

# OAuth2 Configuration
AUTH_SERVER = "http://localhost:5050"  # Authorization Server URL
CLIENT_ID = "myclient"                 # Our client identifier
CLIENT_SECRET = "mysecret"             # Our client secret
REDIRECT_URI = "http://localhost:5052/callback"  # Where to receive the auth code

@app.route('/')
def index():
    """Homepage with login button"""
    logger.info("User accessed the homepage")
    return render_template('index.html')

@app.route('/start_oauth')
def start_oauth():
    """
    Step 1: Begin OAuth Flow
    
    When user clicks "Login", we redirect them to the authorization server.
    We include:
    - client_id: To identify our application
    - redirect_uri: Where to send the user after authorization
    """
    logger.info("=== Step 1: Starting OAuth Flow ===")
    
    # Construct the authorization URL
    auth_url = f"{AUTH_SERVER}/authorize?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}"
    
    logger.info(f"Redirecting user to authorization server: {auth_url}")
    return redirect(auth_url)

@app.route('/callback')
def callback():
    """
    Step 2: Handle Authorization Response
    
    The auth server redirects back here with:
    - code: The authorization code (if user approved)
    - error: Error message (if user denied or other error)
    """
    logger.info("=== Step 2: Received Callback from Auth Server ===")
    
    # 1. Get the authorization code
    auth_code = request.args.get('code')
    if not auth_code:
        logger.error("No authorization code received")
        return "Authorization failed - no code received", 400

    logger.info(f"Received authorization code: {auth_code}")
    
    # 2. Exchange the authorization code for an access token
    logger.info("=== Step 3: Exchanging Auth Code for Access Token ===")
    
    token_response = requests.post(
        f"{AUTH_SERVER}/token",
        json={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "auth_code": auth_code
        }
    )

    if token_response.status_code != 200:
        logger.error(f"Failed to get access token: {token_response.text}")
        return f"Failed to get access token: {token_response.text}", 400

    # 3. Store the access token
    access_token = token_response.json()['access_token']
    session['access_token'] = access_token
    
    logger.info("Successfully obtained and stored access token")
    
    # 4. Get protected user data from resource server
    logger.info("=== Step 4: Accessing Protected Resource ===")
    resource_response = requests.get(
        "http://localhost:5051/api/user-data",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    
    if resource_response.status_code != 200:
        logger.error(f"Failed to get user data: {resource_response.text}")
        user_data = None
    else:
        user_data = resource_response.json()['data']
        logger.info("Successfully retrieved user data from resource server")
    
    logger.info("OAuth flow completed successfully!")
    
    # Render success page with all the details
    return render_template('success.html',
                         client_id=CLIENT_ID,
                         redirect_uri=REDIRECT_URI,
                         auth_code=auth_code,
                         access_token=access_token,
                         user_data=user_data)

if __name__ == '__main__':
    logger.info("Starting OAuth 2.0 Client Application on port 5052")
    app.run(port=5052, debug=True)
