import multiprocessing
import uvicorn
import os
import webbrowser
import time
from dotenv import load_dotenv
import logging
from fasthtml.common import *
import threading
from components import (
    ApiCard, ApiForm, get_styles, get_scripts,
    get_level1_fields, get_level2_fields,
    get_level3_register_fields, get_level3_login_fields, get_level3_predict_fields
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize FastHTML app
app, rt = fast_app()

@rt("/")
def home():
    return (
        Title("Security API Demo"),
        get_styles(),
        get_scripts(),
        Div(
            H1("API Security Demonstration"),
            Div(
                Button("Level 1: Basic Encryption", onclick="switchTab(1)", cls="tab", **{"data-tab": "1"}),
                Button("Level 2: Environment Variables", onclick="switchTab(2)", cls="tab", **{"data-tab": "2"}),
                Button("Level 3: JWT Authentication", onclick="switchTab(3)", cls="tab", **{"data-tab": "3"}),
                cls="tabs"
            ),
            # Level 1
            Div(
                ApiCard(
                    "Level 1: Basic Encryption",
                    "Basic implementation with embedded encryption key (not recommended for production)",
                    ["Simple Fernet encryption", "Key embedded in code", "Basic data protection"],
                    ["Move encryption key to environment variables", "Implement proper key rotation", "Add request validation"],
                    '''curl -X POST "http://localhost:8001/predict/" -H "Content-Type: application/json" -d '{"data": "secret"}'
curl -X POST "http://localhost:8001/decrypt/" -H "Content-Type: application/json" -d '{"encrypted_data": "..."}'
''',
                    8001
                ),
                H3("Try it out:"),
                ApiForm("level1Form", "Submit", "submitLevel1Form()", get_level1_fields()),
                Div(id="level1Result", cls="result-container"),
                id="level1",
                cls="tab-content"
            ),
            # Level 2
            Div(
                ApiCard(
                    "Level 2: Environment Variables",
                    "Improved security with environment variable-based key management",
                    ["Encryption key in .env file", "Better key management", "Improved security practices"],
                    ["Implement key rotation", "Add request validation", "Add rate limiting"],
                    '''curl -X POST "http://localhost:8002/predict/" -H "Content-Type: application/json" -d '{"data": "secret"}'
curl -X POST "http://localhost:8002/decrypt/" -H "Content-Type: application/json" -d '{"encrypted_data": "..."}'
''',
                    8002
                ),
                H3("Try it out:"),
                ApiForm("level2Form", "Submit", "submitLevel2Form()", get_level2_fields()),
                Div(id="level2Result", cls="result-container"),
                id="level2",
                cls="tab-content"
            ),
            # Level 3
            Div(
                ApiCard(
                    "Level 3: JWT Authentication",
                    "Advanced security with JWT token-based authentication",
                    ["JWT token authentication", "Protected endpoints", "User management"],
                    ["Add refresh tokens", "Implement token blacklisting", "Add role-based access control"],
                    '''# First, register a new user
curl -X POST "http://localhost:8003/register" -H "Content-Type: application/json" -d '{
    "username": "testuser",
    "first_name": "Test",
    "last_name": "User",
    "password": "password123"
}'

# Then, get a token
curl -X POST "http://localhost:8003/token" -d "username=testuser&password=password123"

# Finally, make predictions with the token
curl -X POST "http://localhost:8003/predict/" -H "Authorization: Bearer YOUR_TOKEN" -H "Content-Type: application/json" -d '{
    "age": 25,
    "sex": "Female",
    "favorite_color": "Purple",
    "favorite_food": "Sushi"
}'
''',
                    8003
                ),
                H3("Step 1: Register"),
                ApiForm("level3RegisterForm", "Register", "submitLevel3Register()", get_level3_register_fields()),
                H3("Step 2: Login"),
                ApiForm("level3LoginForm", "Login", "submitLevel3Login()", get_level3_login_fields()),
                H3("Step 3: Make Prediction"),
                ApiForm(
                    "level3PredictForm",
                    "Predict",
                    "submitLevel3Predict()",
                    get_level3_predict_fields(),
                ),
                Div(id="level3Result", cls="result-container"),
                id="level3",
                cls="tab-content"
            ),
            cls="container"
        )
    )

def run_level1():
    logger.info("Starting Level 1 API server...")
    uvicorn.run("1_clear_embedded_encryption:app", host="0.0.0.0", port=8001, reload=False)

def run_level2():
    logger.info("Starting Level 2 API server...")
    uvicorn.run("2_enc_key_in_env:app", host="0.0.0.0", port=8002, reload=False)

def run_level3():
    logger.info("Starting Level 3 API server...")
    uvicorn.run("3_exemple_jwt:app", host="0.0.0.0", port=8003, reload=False)

def open_browser():
    time.sleep(2)  # Wait for servers to start
    webbrowser.open("http://localhost:5001")

if __name__ == "__main__":
    try:
        # Start APIs in separate processes
        api1 = multiprocessing.Process(target=run_level1)
        api2 = multiprocessing.Process(target=run_level2)
        api3 = multiprocessing.Process(target=run_level3)
        browser = threading.Thread(target=open_browser)

        api1.start()
        api2.start()
        api3.start()
        browser.start()

        # Start FastHTML app
        uvicorn.run("run_all_apis:app", host="0.0.0.0", port=5001, reload=False)

    except KeyboardInterrupt:
        logger.info("Shutting down...")
        api1.terminate()
        api2.terminate()
        api3.terminate()
