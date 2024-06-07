# Securing API

## Setup

```sh
python -m venv venv
source  venv/bin/activate
pip install -r requirements.txt
```

## Securing attempt 1 `clear_embedded_encryption.py`

example 1 : la clé d'encodage en clair --> mauvaise pratique

```sh
# Running the script
python clear_embedded_encryption.py
```

### testing the API :
To test the API, you can use various tools such as `curl`, Postman, or Python scripts. Below, I'll provide examples for each method to test the `/predict/`, `/pseudonymize/`, and `/decrypt/{user_id}` endpoints.

#### Using `curl`

1. **Test `/predict/` endpoint:**

```sh
curl -X POST "http://localhost:8000/predict/" -H "Content-Type: application/json" -d '{
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@example.com",
    "age": 30,
    "sex": "Male",
    "favorite_color": "Red",
    "favorite_food": "Pizza"
}'
```

2. **Test `/pseudonymize/` endpoint:**

```sh
curl -X GET "http://localhost:8000/pseudonymize/"
```

3. **Test `/decrypt/{user_id}` endpoint (replace `{user_id}` with an actual user ID, e.g., `0`):**

```sh
curl -X GET "http://localhost:8000/decrypt/0"
```

#### Using Postman

1. **Test `/predict/` endpoint:**
    - Open Postman.
    - Create a new POST request with URL: `http://localhost:8000/predict/`.
    - Set the request body to `raw` and `JSON` format.
    - Use the following JSON body:

    ```json
    {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "age": 30,
        "sex": "Male",
        "favorite_color": "Red",
        "favorite_food": "Pizza"
    }
    ```

    - Click `Send`.

2. **Test `/pseudonymize/` endpoint:**
    - Create a new GET request with URL: `http://localhost:8000/pseudonymize/`.
    - Click `Send`.

3. **Test `/decrypt/{user_id}` endpoint:**
    - Create a new GET request with URL: `http://localhost:8000/decrypt/0` (assuming `0` is the user ID).
    - Click `Send`.

#### Using Python Script

1. **Test `/predict/` endpoint:**

```python
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
```

2. **Test `/pseudonymize/` endpoint:**

```python
import requests

url = "http://localhost:8000/pseudonymize/"
response = requests.get(url)
print(response.json())
```

3. **Test `/decrypt/{user_id}` endpoint:**

```python
import requests

url = "http://localhost:8000/decrypt/0"
response = requests.get(url)
print(response.json())
```

## Securing attempt 2
 
Même code mais avec une clé non présente en clair  et utilisation d'un fichier `.env` dans laquel on va stoquer la clée de chiffrement.

Bien pour lors de la phase de prototypage mais meilleur avec la clé enregistrée dans les secret github par exemple.

## OAuth simple : Avec password bearer (script `example_oauth.py`)

OAuth = Ensemble de protocole (auth-code utilisé avec plusieurs app qui intéagisse en même temps).

Pour l'utilisation suivre le processe ci-dessous

1. lancer l'API : `python 3_exemple_oauth`
2. enregistrer un user sur le endpoint `register/` : `ssime:test` (username:password déjà défini)
3. s'authentifier avec les creds ci-dessus : 
![alt text](image.png)
5. Tester la route `./prédict`
4. La route `token` est tout simplement le moyen de s'authentifier de manière programmatique
![alt text](image-1.png)
## OAuth entre plusieurs applications

Voir [slides](https://docs.google.com/presentation/d/1LmQAB2wKJdoj7cNDC6G40Jfd6m3r5xt_/edit#slide=id.g2c6c8d033b1_0_64)