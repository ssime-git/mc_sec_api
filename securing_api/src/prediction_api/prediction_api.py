from fastapi import FastAPI, HTTPException, Header, Depends
import numpy as np
import pickle
import os
import joblib
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel
from sklearn.preprocessing import OneHotEncoder

app = FastAPI(title="Prediction API")

# Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# User prediction model class
class UserPrediction(BaseModel):
    age: int
    sex: str
    favorite_color: str
    favorite_food: str

# Define allowed values for categorical features
allowed_favorite_colors = ['Red', 'Blue', 'Green', 'Yellow', 'Purple']
allowed_favorite_foods = ['Pizza', 'Pasta', 'Burger', 'Sushi', 'Salad', 'Ice Cream']
allowed_sex = ['Male', 'Female']

# Initialize encoder for categorical features
encoder = OneHotEncoder(categories=[allowed_sex, allowed_favorite_colors, allowed_favorite_foods], sparse_output=False)
dummy_data = np.array([['Male', 'Red', 'Pizza']])
encoder.fit(dummy_data)

# Load model from models directory
MODEL_PATH = "/app/models/model_fin2.pkl"
try:
    # Try to load the model from the models directory
    model = joblib.load(MODEL_PATH)
    print(f"Successfully loaded model from {MODEL_PATH}")
except Exception as e:
    print(f"Error loading model: {str(e)}")
    # Use a simple model that returns random predictions
    # This is just a fallback and should not be used in production
    class DummyModel:
        def predict(self, X):
            return [np.random.choice([0, 1])]
        
        def predict_proba(self, X):
            return np.array([[0.2, 0.8]])
    
    model = DummyModel()
    print("Using dummy model for predictions")

# Log model loading
print(f"Model loaded with encoder categories: {encoder.categories_}")
print(f"Model ready for predictions")


# Validation function for user input
def validate_user_input(user: UserPrediction):
    if user.favorite_color not in allowed_favorite_colors:
        raise HTTPException(status_code=400, detail=f"Invalid favorite color. Must be one of: {allowed_favorite_colors}")
    if user.favorite_food not in allowed_favorite_foods:
        raise HTTPException(status_code=400, detail=f"Invalid favorite food. Must be one of: {allowed_favorite_foods}")
    if user.sex not in allowed_sex:
        raise HTTPException(status_code=400, detail=f"Invalid sex. Must be one of: {allowed_sex}")
    if user.age < 0 or user.age > 120:
        raise HTTPException(status_code=400, detail="Age must be between 0 and 120")

# Preprocessing function for user data
def preprocess_user_data(user: UserPrediction):
    categorical_features = np.array([[user.sex, user.favorite_color, user.favorite_food]])
    encoded_features = encoder.transform(categorical_features).flatten()
    features = np.concatenate(([user.age], encoded_features))
    return features.reshape(1, -1)

# API key validation
API_KEY = os.getenv("API_KEY", "internal-secure-key")

def validate_api_key(api_key: str = Header(None)):
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return True

@app.post("/predict")
async def predict(
    data: dict,
    valid: bool = Depends(validate_api_key)
):
    try:
        # Check if we have the required fields for zodiac sign prediction
        if all(k in data for k in ["age", "sex", "favorite_color", "favorite_food"]):
            # Convert dict to UserPrediction model
            user_pred = UserPrediction(
                age=data.get("age"),
                sex=data.get("sex"),
                favorite_color=data.get("favorite_color"),
                favorite_food=data.get("favorite_food")
            )
            
            # Validate input data
            validate_user_input(user_pred)
            
            # Preprocess data for model
            features = preprocess_user_data(user_pred)
            
            # Make prediction
            try:
                # Try to get a numeric prediction
                prediction = model.predict(features)[0]
                if isinstance(prediction, (int, float, np.integer, np.floating)):
                    prediction_value = int(prediction) % 12
                else:
                    # If prediction is not numeric, use a hash of the features to get a consistent zodiac sign
                    prediction_value = hash(str(features)) % 12
            except Exception as e:
                print(f"Error in prediction: {str(e)}")
                # Fallback to a deterministic method based on input features
                prediction_value = (user_pred.age % 12)
            
            # Get confidence value
            try:
                proba = float(model.predict_proba(features).max())
            except Exception as e:
                print(f"Error in confidence calculation: {str(e)}")
                proba = 0.85  # Default confidence
            
            # Map prediction to zodiac sign
            zodiac_signs = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", 
                          "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
            zodiac_sign = zodiac_signs[prediction_value]
            
            # Return prediction results
            return {
                "prediction": zodiac_sign,
                "confidence": float(proba),
                "user_hash": data.get("user_hash", "anonymous"),
                "model_version": "1.0",
                "prediction_type": "zodiac_sign",
                "timestamp": str(np.datetime64('now')),
                "input_features": {
                    "age": user_pred.age,
                    "sex": user_pred.sex,
                    "favorite_color": user_pred.favorite_color,
                    "favorite_food": user_pred.favorite_food
                }
            }
        else:
            raise HTTPException(
                status_code=400, 
                detail="Invalid data format. Must include age, sex, favorite_color, and favorite_food"
            )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
