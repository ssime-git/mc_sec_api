import requests

BASE_URL = "http://localhost:8000"

def register_user(user_data):
    response = requests.post(f"{BASE_URL}/register", json=user_data)
    print("Registration Response:", response.json())
    return response.json()

def get_token(username, password):
    response = requests.post(
        f"{BASE_URL}/token",
        data={"username": username, "password": password}
    )
    return response.json()["access_token"]

def make_prediction(token, prediction_data):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(
        f"{BASE_URL}/predict/",
        json=prediction_data,
        headers=headers
    )
    return response.json()

def main():
    # 1. Register an admin
    admin_data = {
        "username": "admin1",
        "first_name": "Admin",
        "last_name": "User",
        "password": "admin123",
        "role": "admin"
    }
    register_user(admin_data)

    # 2. Register a regular user
    user_data = {
        "username": "user1",
        "first_name": "Regular",
        "last_name": "User",
        "password": "user123",
        "role": "user"
    }
    register_user(user_data)

    # 3. Get admin token
    admin_token = get_token("admin1", "admin123")
    print("Admin Token:", admin_token)

    # 4. Get user token
    user_token = get_token("user1", "user123")
    print("User Token:", user_token)

    # 5. Make prediction
    prediction_data = {
        "age": 25,
        "sex": "Male",
        "favorite_color": "Blue",
        "favorite_food": "Pizza"
    }

    # Try with both admin and user tokens
    admin_prediction = make_prediction(admin_token, prediction_data)
    print("Admin Prediction:", admin_prediction)

    user_prediction = make_prediction(user_token, prediction_data)
    print("User Prediction:", user_prediction)

if __name__ == "__main__":
    main()
