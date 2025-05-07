from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
import os
from apscheduler.schedulers.background import BackgroundScheduler

# Import modules
from gdpr_utils import GDPRUtils
from consent_manager import ConsentManager, ConsentRecord
from user_db import init_db, register_user, get_user, verify_user

# Initialize database
init_db()

# Initialize modules
gdpr = GDPRUtils(retention_days=30)
consent_manager = ConsentManager(required_consents=["data_processing", "data_storage"])

# Security setup
SECRET_KEY = os.getenv("SECRET_KEY", "your-secure-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI(title="Security & GDPR API")

# Registration endpoint
@app.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user_data: dict):
    try:
        username = user_data["username"]
        password = user_data["password"]
        if not register_user(username, password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )
        # Grant default consents using add_consent method
        for consent_type in consent_manager.required_consents:
            consent_manager.add_consent(
                user_id=username,
                consent_type=consent_type,
                granted=True
            )
        gdpr.log_action("user_registered", username)
        return {"message": "User created successfully"}
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Missing username or password"
        )

# Helper functions
def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str):
    return pwd_context.hash(password)

def authenticate_user(username: str, password: str):
    """Authenticate user using verify_user from user_db"""
    return verify_user(username, password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# GDPR Endpoints
@app.post("/consent")
async def give_consent(
    consent_type: str,
    granted: bool,
    expires_days: Optional[int] = None,
    token: str = Depends(oauth2_scheme)
):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        consent_manager.add_consent(username, consent_type, granted, expires_days)
        gdpr.log_action("consent_update", username, f"type={consent_type} granted={granted}")
        return {"status": "success"}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.get("/consents")
async def get_consents(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        return consent_manager.get_user_consents(username)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.delete("/user/data")
async def delete_user_data(
    token: str = Depends(oauth2_scheme),
    confirmation: str = None
):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        if confirmation != "I confirm permanent deletion":
            return {
                "status": "confirmation_required",
                "message": "Please confirm deletion by adding 'I confirm permanent deletion'"
            }
        
        # In a real system, actually delete user data here
        gdpr.log_action("data_deletion", username, "all data deleted")
        return {"status": "success", "message": "All user data deleted"}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Check consents - use the validate_consents method instead
    if not consent_manager.validate_consents(form_data.username):
        raise HTTPException(
            status_code=403,
            detail="Missing required consents"
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": form_data.username},
        expires_delta=access_token_expires
    )
    gdpr.log_action("user_login", form_data.username)
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/pseudonymize")
async def pseudonymize(
    data: dict,
    token: str = Depends(oauth2_scheme)
):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        
        pseudonymized = gdpr.pseudonymize_data(data, username)
        gdpr.log_action("pseudonymization", username, "data pseudonymized")
        return pseudonymized
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.post("/forward-to-prediction")
async def forward_to_prediction(
    data: dict,
    token: str = Depends(oauth2_scheme)
):
    try:
        # Verify token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        
        # Check consents
        if not consent_manager.validate_consents(username):
            raise HTTPException(status_code=403, detail="Missing required consents")
        
        # Validate zodiac sign prediction data format
        if not all(k in data for k in ["age", "sex", "favorite_color", "favorite_food"]):
            raise HTTPException(
                status_code=400, 
                detail="Invalid data format. Must include age, sex, favorite_color, and favorite_food"
            )
            
        # Validate data values
        if not isinstance(data.get("age"), int) or data.get("age") < 0 or data.get("age") > 120:
            raise HTTPException(status_code=400, detail="Age must be a number between 0 and 120")
            
        allowed_sex = ["Male", "Female"]
        if data.get("sex") not in allowed_sex:
            raise HTTPException(status_code=400, detail=f"Sex must be one of: {allowed_sex}")
            
        allowed_colors = ["Red", "Blue", "Green", "Yellow", "Purple"]
        if data.get("favorite_color") not in allowed_colors:
            raise HTTPException(status_code=400, detail=f"Favorite color must be one of: {allowed_colors}")
            
        allowed_foods = ["Pizza", "Pasta", "Burger", "Sushi", "Salad", "Ice Cream"]
        if data.get("favorite_food") not in allowed_foods:
            raise HTTPException(status_code=400, detail=f"Favorite food must be one of: {allowed_foods}")
        
        # Prepare data for prediction - these are not PII so we don't need to pseudonymize them
        pseudonymized_data = {
            "age": data.get("age"),
            "sex": data.get("sex"),
            "favorite_color": data.get("favorite_color"),
            "favorite_food": data.get("favorite_food"),
            "user_hash": username  # Add username as a pseudonymized reference
        }
        
        # Log the prediction request
        gdpr.log_action("prediction_request", username, f"Data format: {list(data.keys())}")
        
        # Forward to prediction API
        prediction_api_url = os.getenv("PREDICTION_API_URL", "http://prediction_api:8001")
        prediction_api_key = os.getenv("PREDICTION_API_KEY", "internal-secure-key")
        
        # Make request to prediction API
        import requests
        response = requests.post(
            f"{prediction_api_url}/predict",
            json=pseudonymized_data,
            headers={"api-key": prediction_api_key}  # FastAPI converts header names to lowercase with hyphens
        )
        
        if response.status_code != 200:
            gdpr.log_action("prediction_error", username, f"Error: {response.status_code}")
            raise HTTPException(status_code=response.status_code, detail=response.json())
        
        gdpr.log_action("prediction", username, "prediction made with pseudonymized data")
        return response.json()
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error connecting to prediction API: {str(e)}")

@app.get("/user/data")
async def get_user_data(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        
        # In a real system, you would fetch actual user data here
        gdpr.log_action("data_access", username)
        return {"username": username}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


# Test endpoint for data retention - only for testing purposes
@app.post("/test/expired-consent")
def test_expired_consent(consent_type: str, token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        
        # Create a consent with expiration date in the past (yesterday)
        conn = user_db.get_db_connection()
        try:
            yesterday = (datetime.now() - timedelta(days=1)).isoformat()
            conn.execute(
                """
                INSERT INTO consents (username, consent_type, granted, granted_at, expires_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(username, consent_type) DO UPDATE SET
                    granted = ?,
                    granted_at = CURRENT_TIMESTAMP,
                    expires_at = ?
                """,
                (username, consent_type, True, datetime.now().isoformat(), yesterday, 
                True, yesterday)
            )
            
            # Log the consent action
            conn.execute(
                "INSERT INTO audit_log (action_type, username, details) VALUES (?, ?, ?)",
                ("consent_granted", username, f"Test expired consent: {consent_type}")
            )
            
            conn.commit()
            return {"success": True, "message": f"Test expired consent created: {consent_type}", "expires_at": yesterday}
        finally:
            conn.close()
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Set up scheduled cleanup job for data retention
scheduler = BackgroundScheduler()
scheduler.add_job(
    consent_manager.cleanup_expired_consents,
    'interval',
    hours=24,  # Run daily
    id='cleanup_expired_data'
)

# Start the scheduler when the application starts
@app.on_event("startup")
def start_scheduler():
    scheduler.start()
    print("Data retention scheduler started - will clean up expired data every 24 hours")

# Shutdown the scheduler when the application stops
@app.on_event("shutdown")
def shutdown_scheduler():
    scheduler.shutdown()
