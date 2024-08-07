import requests
import json

# Set API URL and endpoint
api_url = "http://localhost:8000"
endpoint = "/predict"

# Set authentication details (replace with your own)
username = "ssime"
password = "test"

# Send login request to get an access token
auth_response = requests.post(api_url + "/token", data={"username": username, "password": password})
# Extract the access token from the response
access_token = json.loads(auth_response.text)["access_token"]

# Set headers for authenticated request
headers = {"Authorization": f"Bearer {access_token}"}

# Set API URL and endpoint
url = api_url + endpoint

# Set user data (replace with your own)
data = {
    "age": 30,
    "sex": "Male",
    "favorite_color": "Red",
    "favorite_food": "Pizza"
}

# Send request to predict endpoint with access token
response = requests.post(url, json=data, headers=headers)

# Print response (should contain the predicted astrological sign)
print(response.text)
