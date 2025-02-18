import multiprocessing
import uvicorn
import os
import webbrowser
import time
from dotenv import load_dotenv
import logging
from fasthtml.common import *
import threading
import json

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize FastHTML app
app, rt = fast_app()

def create_code_block(code, language="bash"):
    return Div(
        Pre(Code(code, cls=language)),
        cls="code-block"
    )

def create_api_card(title, description, features, improvements, sample_data, port):
    return Div(
        H2(title),
        P(description),
        H3("Features"),
        Ul(*[Li(feature) for feature in features]),
        
        H3("Sample Request"),
        create_code_block(sample_data),
        
        H3("Potential Improvements"),
        Ul(*[Li(improvement) for improvement in improvements]),
        
        A("Try API", href=f"http://localhost:{port}/docs", cls="button"),
        cls="card"
    )

@rt("/")
def home():
    return (
        Title("Security API Demo"),
        Style("""
            body { 
                background: #1a1a1a; 
                color: #fff; 
                font-family: system-ui; 
                margin: 0; 
                padding: 2rem;
            }
            .container {
                max-width: 900px;
                margin: 0 auto;
            }
            h1 {
                color: #3498db;
                text-align: center;
                font-size: 2.5rem;
                margin-bottom: 2rem;
            }
            .card {
                background: #2d2d2d;
                border-radius: 8px;
                padding: 1.5rem;
                margin-bottom: 2rem;
            }
            h2 { color: #2ecc71; }
            h3 { color: #e74c3c; margin-top: 1.5rem; }
            ul { 
                list-style-type: none; 
                padding-left: 1rem;
                margin-bottom: 1.5rem;
            }
            li::before {
                content: "•";
                color: #3498db;
                font-weight: bold;
                display: inline-block;
                width: 1em;
                margin-left: -1em;
            }
            .button {
                display: inline-block;
                padding: 0.8rem 1.5rem;
                background: #3498db;
                color: white;
                text-decoration: none;
                border-radius: 4px;
                transition: background 0.3s ease;
            }
            .button:hover {
                background: #2980b9;
            }
            .code-block {
                background: #1a1a1a;
                border-radius: 4px;
                padding: 1rem;
                margin: 1rem 0;
            }
            .tabs {
                display: flex;
                gap: 1rem;
                margin-bottom: 2rem;
            }
            .tab {
                padding: 0.8rem 1.5rem;
                background: #2d2d2d;
                border: none;
                color: white;
                cursor: pointer;
                border-radius: 4px;
                transition: background 0.3s ease;
            }
            .tab:hover, .tab.active {
                background: #3498db;
            }
            .tab-content {
                display: none;
            }
            .tab-content.active {
                display: block;
            }
            .form-group {
                margin-bottom: 1rem;
            }
            .form-group label {
                display: block;
                margin-bottom: 0.5rem;
                color: #3498db;
            }
            .form-group input, .form-group select {
                width: 100%;
                padding: 0.5rem;
                border: 1px solid #3498db;
                border-radius: 4px;
                background: #2d2d2d;
                color: white;
            }
            .form-group select option {
                background: #2d2d2d;
            }
            .result-container {
                background: #2d2d2d;
                border-radius: 8px;
                padding: 1.5rem;
                margin-top: 1rem;
                border: 1px solid #3498db;
            }
            .result-container pre {
                margin: 0;
                white-space: pre-wrap;
                word-wrap: break-word;
            }
        """),
        Script("""
            function switchTab(level) {
                document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
                document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
                document.querySelector(`[data-tab="${level}"]`).classList.add('active');
                document.querySelector(`#level${level}`).classList.add('active');
            }
            
            async function submitLevel1Form() {
                const form = document.getElementById('level1Form');
                const resultDiv = document.getElementById('level1Result');
                
                const formData = {
                    first_name: form.first_name.value,
                    last_name: form.last_name.value,
                    email: form.email.value,
                    age: parseInt(form.age.value),
                    sex: form.sex.value,
                    favorite_color: form.favorite_color.value,
                    favorite_food: form.favorite_food.value
                };
                
                try {
                    const response = await fetch('http://localhost:8000/predict/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify(formData)
                    });
                    
                    const data = await response.json();
                    
                    if (response.ok) {
                        resultDiv.innerHTML = `
                            <h3>Results:</h3>
                            <pre>
Astrological Sign: ${data.astrological_sign}

Encrypted Data:
- First Name: ${data.encrypted_first_name}
- Last Name: ${data.encrypted_last_name}
- Email: ${data.encrypted_email}
                            </pre>
                        `;
                    } else {
                        resultDiv.innerHTML = `<h3>Error:</h3><pre>${JSON.stringify(data, null, 2)}</pre>`;
                    }
                } catch (error) {
                    resultDiv.innerHTML = `<h3>Error:</h3><pre>${error.message}</pre>`;
                }
            }
            
            async function submitLevel2Form() {
                const form = document.getElementById('level2Form');
                const resultDiv = document.getElementById('level2Result');
                
                const formData = {
                    first_name: form.first_name2.value,
                    last_name: form.last_name2.value,
                    email: form.email2.value,
                    age: parseInt(form.age2.value),
                    sex: form.sex2.value,
                    favorite_color: form.favorite_color2.value,
                    favorite_food: form.favorite_food2.value
                };
                
                try {
                    const response = await fetch('http://localhost:8002/predict/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify(formData)
                    });
                    
                    const data = await response.json();
                    
                    if (response.ok) {
                        resultDiv.innerHTML = `
                            <h3>Results:</h3>
                            <pre>
Astrological Sign: ${data.astrological_sign}

Encrypted Data (using environment key):
- First Name: ${data.encrypted_first_name}
- Last Name: ${data.encrypted_last_name}
- Email: ${data.encrypted_email}
                            </pre>
                        `;
                    } else {
                        resultDiv.innerHTML = `<h3>Error:</h3><pre>${JSON.stringify(data, null, 2)}</pre>`;
                    }
                } catch (error) {
                    resultDiv.innerHTML = `<h3>Error:</h3><pre>${error.message}</pre>`;
                }
            }
            
            async function submitLevel3Register() {
                const form = document.getElementById('level3RegisterForm');
                const resultDiv = document.getElementById('level3Result');
                
                const formData = {
                    username: form.username.value,
                    first_name: form.first_name3.value,
                    last_name: form.last_name3.value,
                    password: form.password.value
                };
                
                try {
                    const response = await fetch('http://localhost:8003/register', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify(formData)
                    });
                    
                    const data = await response.json();
                    
                    if (response.ok) {
                        resultDiv.innerHTML = `
                            <h3>Registration Successful!</h3>
                            <pre>
User ${formData.username} has been registered.
Please login to get your access token.
                            </pre>
                        `;
                    } else {
                        resultDiv.innerHTML = `<h3>Error:</h3><pre>${JSON.stringify(data, null, 2)}</pre>`;
                    }
                } catch (error) {
                    resultDiv.innerHTML = `<h3>Error:</h3><pre>${error.message}</pre>`;
                }
            }

            async function submitLevel3Login() {
                const form = document.getElementById('level3LoginForm');
                const resultDiv = document.getElementById('level3Result');
                
                const formData = new URLSearchParams();
                formData.append('username', form.username_login.value);
                formData.append('password', form.password_login.value);
                
                try {
                    const response = await fetch('http://localhost:8003/token', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/x-www-form-urlencoded',
                        },
                        body: formData
                    });
                    
                    const data = await response.json();
                    
                    if (response.ok) {
                        // Store token in localStorage
                        localStorage.setItem('jwt_token', data.access_token);
                        resultDiv.innerHTML = `
                            <h3>Login Successful!</h3>
                            <pre>
Access token received and stored.
You can now make predictions!
                            </pre>
                        `;
                        // Show the prediction form
                        document.getElementById('level3PredictForm').style.display = 'block';
                    } else {
                        resultDiv.innerHTML = `<h3>Error:</h3><pre>${JSON.stringify(data, null, 2)}</pre>`;
                    }
                } catch (error) {
                    resultDiv.innerHTML = `<h3>Error:</h3><pre>${error.message}</pre>`;
                }
            }

            async function submitLevel3Predict() {
                const form = document.getElementById('level3PredictForm');
                const resultDiv = document.getElementById('level3Result');
                const token = localStorage.getItem('jwt_token');
                
                if (!token) {
                    resultDiv.innerHTML = `<h3>Error:</h3><pre>Please login first to get an access token.</pre>`;
                    return;
                }
                
                const formData = {
                    age: parseInt(form.age3.value),
                    sex: form.sex3.value,
                    favorite_color: form.favorite_color3.value,
                    favorite_food: form.favorite_food3.value
                };
                
                try {
                    const response = await fetch('http://localhost:8003/predict/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'Authorization': `Bearer ${token}`
                        },
                        body: JSON.stringify(formData)
                    });
                    
                    const data = await response.json();
                    
                    if (response.ok) {
                        resultDiv.innerHTML = `
                            <h3>Prediction Results:</h3>
                            <pre>
Astrological Sign: ${data.astrological_sign}
                            </pre>
                        `;
                    } else {
                        if (response.status === 401) {
                            localStorage.removeItem('jwt_token');
                            document.getElementById('level3PredictForm').style.display = 'none';
                            resultDiv.innerHTML = `<h3>Error:</h3><pre>Token expired. Please login again.</pre>`;
                        } else {
                            resultDiv.innerHTML = `<h3>Error:</h3><pre>${JSON.stringify(data, null, 2)}</pre>`;
                        }
                    }
                } catch (error) {
                    resultDiv.innerHTML = `<h3>Error:</h3><pre>${error.message}</pre>`;
                }
            }
            
            // Initialize with first tab active
            document.addEventListener('DOMContentLoaded', () => {
                switchTab(1);
            });
        """),
        Div(
            H1("API Security Demonstration"),
            Div(
                Button("Level 1: Basic Encryption", onclick="switchTab(1)", cls="tab", **{"data-tab": "1"}),
                Button("Level 2: Environment Variables", onclick="switchTab(2)", cls="tab", **{"data-tab": "2"}),
                Button("Level 3: JWT Authentication", onclick="switchTab(3)", cls="tab", **{"data-tab": "3"}),
                cls="tabs"
            ),
            Div(
                create_api_card(
                    "Level 1: Basic Encryption",
                    "Basic implementation with embedded encryption key (not recommended for production)",
                    ["Simple Fernet encryption", "Key embedded in code", "Basic data protection"],
                    ["Move encryption key to environment variables", "Implement proper key rotation", "Add request validation"],
                    '''curl -X POST "http://localhost:8000/predict/" -H "Content-Type: application/json" -d '{"data": "secret"}'
curl -X POST "http://localhost:8000/decrypt/" -H "Content-Type: application/json" -d '{"encrypted_data": "..."}'
''',
                    8000
                ),
                H3("Try it out:"),
                Form(
                    Div(
                        Label("First Name:", fr="first_name"),
                        Input(type="text", name="first_name", value="John", id="first_name"),
                        cls="form-group"
                    ),
                    Div(
                        Label("Last Name:", fr="last_name"),
                        Input(type="text", name="last_name", value="Doe", id="last_name"),
                        cls="form-group"
                    ),
                    Div(
                        Label("Email:", fr="email"),
                        Input(type="email", name="email", value="john.doe@example.com", id="email"),
                        cls="form-group"
                    ),
                    Div(
                        Label("Age:", fr="age"),
                        Input(type="number", name="age", value="30", id="age"),
                        cls="form-group"
                    ),
                    Div(
                        Label("Sex:", fr="sex"),
                        Select(
                            Option("Male", value="Male"),
                            Option("Female", value="Female"),
                            name="sex",
                            id="sex"
                        ),
                        cls="form-group"
                    ),
                    Div(
                        Label("Favorite Color:", fr="favorite_color"),
                        Select(
                            Option("Red", value="Red"),
                            Option("Blue", value="Blue"),
                            Option("Green", value="Green"),
                            Option("Yellow", value="Yellow"),
                            Option("Purple", value="Purple"),
                            name="favorite_color",
                            id="favorite_color"
                        ),
                        cls="form-group"
                    ),
                    Div(
                        Label("Favorite Food:", fr="favorite_food"),
                        Select(
                            Option("Pizza", value="Pizza"),
                            Option("Pasta", value="Pasta"),
                            Option("Burger", value="Burger"),
                            Option("Sushi", value="Sushi"),
                            Option("Salad", value="Salad"),
                            Option("Ice Cream", value="Ice Cream"),
                            name="favorite_food",
                            id="favorite_food"
                        ),
                        cls="form-group"
                    ),
                    Button("Submit", type="button", onclick="submitLevel1Form()", cls="button"),
                    id="level1Form"
                ),
                Div(id="level1Result", cls="result-container"),
                id="level1",
                cls="tab-content"
            ),
            Div(
                create_api_card(
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
                Form(
                    Div(
                        Label("First Name:", fr="first_name2"),
                        Input(type="text", name="first_name2", value="Jane", id="first_name2"),
                        cls="form-group"
                    ),
                    Div(
                        Label("Last Name:", fr="last_name2"),
                        Input(type="text", name="last_name2", value="Smith", id="last_name2"),
                        cls="form-group"
                    ),
                    Div(
                        Label("Email:", fr="email2"),
                        Input(type="email", name="email2", value="jane.smith@example.com", id="email2"),
                        cls="form-group"
                    ),
                    Div(
                        Label("Age:", fr="age2"),
                        Input(type="number", name="age2", value="28", id="age2"),
                        cls="form-group"
                    ),
                    Div(
                        Label("Sex:", fr="sex2"),
                        Select(
                            Option("Female", value="Female"),
                            Option("Male", value="Male"),
                            name="sex2",
                            id="sex2"
                        ),
                        cls="form-group"
                    ),
                    Div(
                        Label("Favorite Color:", fr="favorite_color2"),
                        Select(
                            Option("Blue", value="Blue"),
                            Option("Red", value="Red"),
                            Option("Green", value="Green"),
                            Option("Yellow", value="Yellow"),
                            Option("Purple", value="Purple"),
                            name="favorite_color2",
                            id="favorite_color2"
                        ),
                        cls="form-group"
                    ),
                    Div(
                        Label("Favorite Food:", fr="favorite_food2"),
                        Select(
                            Option("Sushi", value="Sushi"),
                            Option("Pizza", value="Pizza"),
                            Option("Pasta", value="Pasta"),
                            Option("Burger", value="Burger"),
                            Option("Salad", value="Salad"),
                            Option("Ice Cream", value="Ice Cream"),
                            name="favorite_food2",
                            id="favorite_food2"
                        ),
                        cls="form-group"
                    ),
                    Button("Submit", type="button", onclick="submitLevel2Form()", cls="button"),
                    id="level2Form"
                ),
                Div(id="level2Result", cls="result-container"),
                id="level2",
                cls="tab-content"
            ),
            Div(
                create_api_card(
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
                Form(
                    Div(
                        Label("Username:", fr="username"),
                        Input(type="text", name="username", value="testuser", id="username"),
                        cls="form-group"
                    ),
                    Div(
                        Label("First Name:", fr="first_name3"),
                        Input(type="text", name="first_name3", value="Test", id="first_name3"),
                        cls="form-group"
                    ),
                    Div(
                        Label("Last Name:", fr="last_name3"),
                        Input(type="text", name="last_name3", value="User", id="last_name3"),
                        cls="form-group"
                    ),
                    Div(
                        Label("Password:", fr="password"),
                        Input(type="password", name="password", value="password123", id="password"),
                        cls="form-group"
                    ),
                    Button("Register", type="button", onclick="submitLevel3Register()", cls="button"),
                    id="level3RegisterForm"
                ),
                H3("Step 2: Login"),
                Form(
                    Div(
                        Label("Username:", fr="username_login"),
                        Input(type="text", name="username_login", value="testuser", id="username_login"),
                        cls="form-group"
                    ),
                    Div(
                        Label("Password:", fr="password_login"),
                        Input(type="password", name="password_login", value="password123", id="password_login"),
                        cls="form-group"
                    ),
                    Button("Login", type="button", onclick="submitLevel3Login()", cls="button"),
                    id="level3LoginForm"
                ),
                H3("Step 3: Make Prediction"),
                Form(
                    Div(
                        Label("Age:", fr="age3"),
                        Input(type="number", name="age3", value="25", id="age3"),
                        cls="form-group"
                    ),
                    Div(
                        Label("Sex:", fr="sex3"),
                        Select(
                            Option("Female", value="Female"),
                            Option("Male", value="Male"),
                            name="sex3",
                            id="sex3"
                        ),
                        cls="form-group"
                    ),
                    Div(
                        Label("Favorite Color:", fr="favorite_color3"),
                        Select(
                            Option("Purple", value="Purple"),
                            Option("Red", value="Red"),
                            Option("Blue", value="Blue"),
                            Option("Green", value="Green"),
                            Option("Yellow", value="Yellow"),
                            name="favorite_color3",
                            id="favorite_color3"
                        ),
                        cls="form-group"
                    ),
                    Div(
                        Label("Favorite Food:", fr="favorite_food3"),
                        Select(
                            Option("Sushi", value="Sushi"),
                            Option("Pizza", value="Pizza"),
                            Option("Pasta", value="Pasta"),
                            Option("Burger", value="Burger"),
                            Option("Salad", value="Salad"),
                            Option("Ice Cream", value="Ice Cream"),
                            name="favorite_food3",
                            id="favorite_food3"
                        ),
                        cls="form-group"
                    ),
                    Button("Predict", type="button", onclick="submitLevel3Predict()", cls="button"),
                    id="level3PredictForm",
                    style="display: none;"
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
    uvicorn.run("1_clear_embedded_encryption:app", host="0.0.0.0", port=8000, reload=False)

def run_level2():
    logger.info("Starting Level 2 API server...")
    uvicorn.run("2_enc_key_in_env:app", host="0.0.0.0", port=8002, reload=False)

def run_level3():
    logger.info("Starting Level 3 API server...")
    uvicorn.run("3_exemple_jwt:app", host="0.0.0.0", port=8003, reload=False)

def open_browser():
    time.sleep(2)  # Wait for servers to start
    webbrowser.open('http://localhost:5001')

if __name__ == "__main__":
    try:
        # Start APIs in separate processes
        api1 = multiprocessing.Process(target=run_level1)
        api2 = multiprocessing.Process(target=run_level2)
        api3 = multiprocessing.Process(target=run_level3)

        logger.info("Starting API servers...")
        api1.start()
        api2.start()
        api3.start()

        # Open browser in a thread
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()

        # Run FastHTML in the main thread
        logger.info("Starting FastHTML server...")
        serve(port=5001)

    except KeyboardInterrupt:
        logger.info("\nShutting down servers...")
        api1.terminate()
        api2.terminate()
        api3.terminate()
        api1.join()
        api2.join()
        api3.join()
        logger.info("All servers have been shut down.")
