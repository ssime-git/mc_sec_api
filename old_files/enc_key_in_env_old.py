from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from cryptography.fernet import Fernet
from sklearn.preprocessing import OneHotEncoder
from dotenv import load_dotenv
import numpy as np
import joblib
import hashlib

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

##########################################
# Load the trained model
model = joblib.load("./models/model_fin2.pkl")

# Create a OneHotEncoder for the categorical features
encoder = OneHotEncoder(categories="auto")

# Define the allowed classes for favorite_color, favorite_food, and sex
allowed_favorite_colors = ['Red', 'Blue', 'Green', 'Yellow', 'Purple']
allowed_favorite_foods = ['Pizza', 'Pasta', 'Burger', 'Sushi', 'Salad', 'Ice Cream']
allowed_sex = ['Male', 'Female']

# Fit the OneHotEncoder with the allowed classes
encoder.fit([[color] for color in allowed_favorite_colors] +
             [[food] for food in allowed_favorite_foods] +
             [[sex] for sex in allowed_sex])

##########################################
# Define the encryption key
load_dotenv()
import os

encryption_key = os.getenv("ENCRYPTION_KEY")
cipher_suite = Fernet(encryption_key)

# Pseudonymization function

#def pseudonymize_data(encrypted_data):
    # Apply hash function (SHA256) to the encrypted data
 #   hashed_data = hashlib.sha256(encrypted_data).hexdigest()
 #   return hashed_data

def pseudonymize_data(encrypted_data):
    # Convert encrypted_data en une chaîne de caractères
    encrypted_data_str = encrypted_data.decode()

    # Apply hash function (SHA256) to the encrypted data
    hashed_data = hashlib.sha256(encrypted_data_str.encode()).hexdigest()
    return hashed_data


def decrypt(encrypted_value):
    plain_text = cipher_suite.decrypt(encrypted_value)
    return plain_text.decode()

###########################################
# In-memory storage for user data
users = []

# Endpoint for predicting astrological sign
@app.post("/predict/")
def predict_sign(user: User):
    # Check if favorite_color, favorite_food, and sex are in the allowed classes
    if user.favorite_color not in allowed_favorite_colors:
        return {"error": "Invalid favorite color"}

    if user.favorite_food not in allowed_favorite_foods:
        return {"error": "Invalid favorite food"}

    if user.sex not in allowed_sex:
        return {"error": "Invalid sex"}

    # Encrypt the user data
    encrypted_first_name = cipher_suite.encrypt(user.first_name.encode())
    encrypted_last_name = cipher_suite.encrypt(user.last_name.encode())
    encrypted_email = cipher_suite.encrypt(user.email.encode())

    # Preprocess the data
    categorical_features = [user.sex, user.favorite_color, user.favorite_food]
    encoded_features = encoder.transform([[category] for category in categorical_features]).toarray()[0]

    # Combine all features
    features = np.concatenate(([user.age], encoded_features))

    # Reshape the features to match the model's input shape
    features = features.reshape(1, -1)

    # Make the prediction
    prediction = model.predict(features)[0]

    # Store the encrypted user data
    users.append({
        "encrypted_first_name": encrypted_first_name,
        "encrypted_last_name": encrypted_last_name,
        "encrypted_email": encrypted_email
    })

    return {
        "astrological_sign": prediction,
        "encrypted_first_name": encrypted_first_name,
        "encrypted_last_name": encrypted_last_name,
        "encrypted_email": encrypted_email
    }

#####

@app.get("/pseudonymize/")
def pseudonymize_user_data():
    pseudonymized_users = []

    # Pseudonymize the encrypted user data
    for user in users:
        pseudonymized_user = {
            "pseudonymized_first_name": pseudonymize_data(user["encrypted_first_name"]),
            "pseudonymized_last_name": pseudonymize_data(user["encrypted_last_name"]),
            "pseudonymized_email": pseudonymize_data(user["encrypted_email"]),
        }

        pseudonymized_users.append(pseudonymized_user)

    return pseudonymized_users



##########################""
@app.get("/decrypt/{user_id}")
def decrypt_data(user_id: int):
    if user_id < 0 or user_id >= len(users):
        return {"error": "User not found"}

    user = users[user_id]

    decrypted_first_name = cipher_suite.decrypt(user["encrypted_first_name"]).decode()
    decrypted_last_name = cipher_suite.decrypt(user["encrypted_last_name"]).decode()
    decrypted_email = cipher_suite.decrypt(user["encrypted_email"]).decode()

    return {
        "user_id": user_id,
        "decrypted_first_name": decrypted_first_name,
        "decrypted_last_name": decrypted_last_name,
        "decrypted_email": decrypted_email
    }


####################################
# Root endpoint
@app.get("/", response_class=HTMLResponse)
def root():
    return """
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

####################################

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("test:app", host="0.0.0.0", port=8000, reload=True)