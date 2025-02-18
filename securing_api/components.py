from fasthtml.common import *

class FormGroup:
    def __init__(self, label_text, input_type="text", input_id=None, input_name=None, value=None, options=None):
        self.label_text = label_text
        self.input_type = input_type
        self.input_id = input_id or input_name
        self.input_name = input_name or input_id
        self.value = value
        self.options = options

    def __ft__(self):
        input_element = (
            Select(
                *[Option(text, value=value) for value, text in self.options],
                name=self.input_name,
                id=self.input_id
            )
            if self.input_type == "select" else
            Input(
                type=self.input_type,
                name=self.input_name,
                value=self.value,
                id=self.input_id
            )
        )
        
        return Div(
            Label(self.label_text, fr=self.input_id),
            input_element,
            cls="form-group"
        )

class ApiForm:
    def __init__(self, form_id, submit_text, submit_function, fields):
        self.form_id = form_id
        self.submit_text = submit_text
        self.submit_function = submit_function
        self.fields = fields

    def __ft__(self):
        return Form(
            *[FormGroup(**field) for field in self.fields],
            Button(self.submit_text, type="button", onclick=self.submit_function, cls="button"),
            id=self.form_id
        )

class ApiCard:
    def __init__(self, title, description, features, improvements, example_code, port):
        self.title = title
        self.description = description
        self.features = features
        self.improvements = improvements
        self.example_code = example_code
        self.port = port

    def __ft__(self):
        return Div(
            H2(self.title),
            P(self.description),
            H3("Features"),
            Ul(*[Li(feature) for feature in self.features]),
            H3("Sample Request"),
            Div(Pre(Code(self.example_code)), cls="code-block"),
            H3("Potential Improvements"),
            Ul(*[Li(improvement) for improvement in self.improvements]),
            A("Try API", href=f"http://localhost:{self.port}/docs", cls="button"),
            cls="card"
        )

# Common form field configurations
def get_level1_fields():
    return [
        {"label_text": "First Name:", "input_name": "first_name", "value": "John"},
        {"label_text": "Last Name:", "input_name": "last_name", "value": "Doe"},
        {"label_text": "Email:", "input_type": "email", "input_name": "email", "value": "john.doe@example.com"},
        {"label_text": "Age:", "input_type": "number", "input_name": "age", "value": "30"},
        {"label_text": "Sex:", "input_type": "select", "input_name": "sex", "options": [("Male", "Male"), ("Female", "Female")]},
        {"label_text": "Favorite Color:", "input_type": "select", "input_name": "favorite_color", 
         "options": [("Red", "Red"), ("Blue", "Blue"), ("Green", "Green"), ("Yellow", "Yellow"), ("Purple", "Purple")]},
        {"label_text": "Favorite Food:", "input_type": "select", "input_name": "favorite_food",
         "options": [("Pizza", "Pizza"), ("Pasta", "Pasta"), ("Burger", "Burger"), ("Sushi", "Sushi"), 
                    ("Salad", "Salad"), ("Ice Cream", "Ice Cream")]}
    ]

def get_level2_fields():
    return [field | {"input_name": f"{field['input_name']}2"} for field in get_level1_fields()]

def get_level3_register_fields():
    return [
        {"label_text": "Username:", "input_name": "username", "value": "testuser"},
        {"label_text": "First Name:", "input_name": "first_name3", "value": "Test"},
        {"label_text": "Last Name:", "input_name": "last_name3", "value": "User"},
        {"label_text": "Password:", "input_type": "password", "input_name": "password", "value": "password123"}
    ]

def get_level3_login_fields():
    return [
        {"label_text": "Username:", "input_name": "username_login", "value": "testuser"},
        {"label_text": "Password:", "input_type": "password", "input_name": "password_login", "value": "password123"}
    ]

def get_level3_predict_fields():
    base_fields = get_level1_fields()[3:]  # Get only age and after
    return [field | {"input_name": f"{field['input_name']}3"} for field in base_fields]

# Styles
def get_styles():
    return Style("""
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
            border: none;
            cursor: pointer;
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
    """)

# Scripts
def get_scripts():
    return Script("""
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
                    localStorage.setItem('jwt_token', data.access_token);
                    resultDiv.innerHTML = `
                        <h3>Login Successful!</h3>
                        <pre>
Access token received and stored.
You can now make predictions!
                        </pre>
                    `;
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
        
        document.addEventListener('DOMContentLoaded', () => {
            switchTab(1);
        });
    """)
