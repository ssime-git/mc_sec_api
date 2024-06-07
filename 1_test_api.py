import requests

url = "http://localhost:8000/predict/"
data = {
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@example.com",
    "age": 30,
    "sex": "Male",
    "favorite_color": "Red",
    "favorite_food": "Pizza"
}
response = requests.post(url, json=data)
print(response.json())