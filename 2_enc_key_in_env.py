import joblib
import hashlib
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from cryptography.fernet import Fernet
from sklearn.preprocessing import OneHotEncoder
import numpy as np

app = FastAPI()

# Define the User input model
class User(BaseModel):
    first_name: str
    last_name: str
    email: str
    age: int
    sex: str
    favorite_color: str
    favorite_food: str

# Functions for initialization and configuration
def load_model(path: str):
    return joblib.load(path)

def initialize_allowed_classes():
    return {
        'favorite_colors': ['Red', 'Blue', 'Green', 'Yellow', 'Purple'],
        'favorite_foods': ['Pizza', 'Pasta', 'Burger', 'Sushi', 'Salad', 'Ice Cream'],
        'sex': ['Male', 'Female']
    }

def create_encoder(allowed_classes):
    encoder = OneHotEncoder(categories=[allowed_classes['sex'], allowed_classes['favorite_colors'], allowed_classes['favorite_foods']], sparse_output=False)
    dummy_data = np.array([['Male', 'Red', 'Pizza']])
    encoder.fit(dummy_data)
    return encoder

def generate_encryption_suite():
    encryption_key = Fernet.generate_key()
    cipher_suite = Fernet(encryption_key)
    return cipher_suite

def initialize_users_storage():
    return []

# Initialization
model = load_model("./models/model_fin2.pkl")
allowed_classes = initialize_allowed_classes()
encoder = create_encoder(allowed_classes)
cipher_suite = generate_encryption_suite()
users = initialize_users_storage()

# Helper functions
def validate_user_input(user: User, allowed_classes):
    if user.favorite_color not in allowed_classes['favorite_colors']:
        raise HTTPException(status_code=400, detail="Invalid favorite color")
    if user.favorite_food not in allowed_classes['favorite_foods']:
        raise HTTPException(status_code=400, detail="Invalid favorite food")
    if user.sex not in allowed_classes['sex']:
        raise HTTPException(status_code=400, detail="Invalid sex")

def encrypt_user_data(user: User, cipher_suite):
    return {
        "encrypted_first_name": cipher_suite.encrypt(user.first_name.encode()),
        "encrypted_last_name": cipher_suite.encrypt(user.last_name.encode()),
        "encrypted_email": cipher_suite.encrypt(user.email.encode())
    }

def preprocess_user_data(user: User, encoder):
    categorical_features = np.array([[user.sex, user.favorite_color, user.favorite_food]])
    encoded_features = encoder.transform(categorical_features).flatten()
    features = np.concatenate(([user.age], encoded_features))
    return features.reshape(1, -1)

def pseudonymize_data(encrypted_data):
    return hashlib.sha256(encrypted_data).hexdigest()

# Endpoints
@app.post("/predict/")
async def predict_sign(user: User):
    validate_user_input(user, allowed_classes)
    encrypted_data = encrypt_user_data(user, cipher_suite)
    features = preprocess_user_data(user, encoder)
    prediction = model.predict(features)[0]

    users.append(encrypted_data)

    return {
        "astrological_sign": prediction,
        "encrypted_first_name": encrypted_data["encrypted_first_name"].decode(),
        "encrypted_last_name": encrypted_data["encrypted_last_name"].decode(),
        "encrypted_email": encrypted_data["encrypted_email"].decode()
    }

@app.get("/pseudonymize/")
async def pseudonymize_user_data():
    pseudonymized_users = [
        {
            "pseudonymized_first_name": pseudonymize_data(user["encrypted_first_name"]),
            "pseudonymized_last_name": pseudonymize_data(user["encrypted_last_name"]),
            "pseudonymized_email": pseudonymize_data(user["encrypted_email"]),
        }
        for user in users
    ]
    return pseudonymized_users

@app.get("/decrypt/{user_id}")
async def decrypt_data(user_id: int):
    if user_id < 0 or user_id >= len(users):
        raise HTTPException(status_code=404, detail="User not found")

    user = users[user_id]
    return {
        "user_id": user_id,
        "decrypted_first_name": cipher_suite.decrypt(user["encrypted_first_name"]).decode(),
        "decrypted_last_name": cipher_suite.decrypt(user["encrypted_last_name"]).decode(),
        "decrypted_email": cipher_suite.decrypt(user["encrypted_email"]).decode()
    }

@app.get("/", response_class=HTMLResponse)
async def root():
    html_content = """
    <html>
    <body>
        <script>
            function showPopup() {
                alert("Thank you for using our service! By clicking the button below, you give your consent for us to use your data for predicting your astrological sign.");
            }
        </script>
        <h1>Welcome to the Astrological Sign Prediction API!</h1>
        <button onclick="showPopup()">Click Me!</button>
    </body>
    </html>
    """
    return html_content

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("2_enc_key_in_env:app", host="0.0.0.0", port=8000, reload=True)
