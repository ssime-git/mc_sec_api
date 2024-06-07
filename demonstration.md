# Introduction

Ce projet est un exemple d'API qui permet de prédir certaines informations à partir d'un ensemble de données utilisateur. L'API est sécurisée par un système de chiffrement et de pseudonymisation.

## Première tentative

```sh
python -m venv venv
source  venv/bin/activate
pip install -r requirements.txt

# Lancement de l'application
python 1_clear_embedded_encryption.py
```

Ouvrez l'API pour la tester.

**Exemple de code Python**

Voici le code Python qui permet de tester l'API :

```python
import requests

# URL de l'API
api_url = "http://localhost:8000"

# Endpoint pour la prévision
endpoint = "/predict"

# Données utilisateur (remplacez par vos propres informations)
data = {
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@example.com",
    "age": 30,
    "sex": "Male",
    "favorite_color": "Red",
    "favorite_food": "Pizza"
}

# Envoi de la requête POST pour la prévision
response = requests.post(api_url + endpoint, json=data)
print(response.json())
```
Ce code envoie une requête POST à l'endpoint `/predict` avec les données utilisateur et imprime le résultat en JSON.

**Méthodes de test**

Il existe plusieurs façons de tester l'API. Voici quelques-unes :

#### Utilisation de `curl`

1. Tester l'endpoint `/predict/` :
```bash
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
2. Tester l'endpoint `/pseudonymize/` :
```bash
curl -X GET "http://localhost:8000/pseudonymize/"
```
3. Tester l'endpoint `/decrypt/{user_id}` (remplacez `{user_id}` par un ID utilisateur valide) :
```bash
curl -X GET "http://localhost:8000/decrypt/0"
```

#### Utilisation de Postman

1. Tester l'endpoint `/predict/` :
     - Ouvrez Postman.
     - Créez une nouvelle requête POST avec URL : `http://localhost:8000/predict/`.
     - Définissez le corps de la requête en tant que `raw` et `JSON` format.
     - Utilisez le corps JSON suivant :

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

     - Cliquez sur `Send`.

2. Tester l'endpoint `/pseudonymize/` :
     - Créez une nouvelle requête GET avec URL : `http://localhost:8000/pseudonymize/`.
     - Cliquez sur `Send`.

3. Tester l'endpoint `/decrypt/{user_id}` :
     - Créez une nouvelle requête GET avec URL : `http://localhost:8000/decrypt/0` (en supposant que `0` est l'ID utilisateur).
     - Cliquez sur `Send`.

#### Utilisation d'un script Python

1. Tester l'endpoint `/predict/` :
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
2. Tester l'endpoint `/pseudonymize/` :
```python
import requests

url = "http://localhost:8000/pseudonymize/"
response = requests.get(url)
print(response.json())
```
3. Tester l'endpoint `/decrypt/{user_id}` (remplacez `{user_id}` par un ID utilisateur valide) :
```python
import requests

url = "http://localhost:8000/decrypt/0"
response = requests.get(url)
print(response.json())
```

**Sécurité**

Pour sécuriser l'API, nous utilisons une clé non présente en clair et un fichier `.env` pour stocker la clée de chiffrement. Cela permet de garantir la sécurité des données utilisateur.


**OAuth simple**
Pour sécuriser l'accès à l'API, nous utilisons un mécanisme d'autorisation simple basé sur OAuth. Pour utiliser l'API, il faut d'abord obtenir un token d'accès en envoyant une requête POST à l'endpoint `/oauth/token`. Le corps de la requête doit contenir les informations suivantes :

* `grant_type`: valeur `password` ou `refresh_token`
* `username`: nom d'utilisateur valide
* `password`: mot de passe du compte utilisateur

Par exemple, si vous voulez obtenir un token d'accès pour le compte `john.doe@example.com` avec le mot de passe `mypassword`, votre requête POST pourrait être la suivante :

```bash
curl -X POST 'http://localhost:8000/oauth/token' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'grant_type=password&username=john.doe@example.com&password=mypassword'
```

Lorsque vous obtiendrez le token d'accès, vous pouvez l'utiliser pour accéder à l'API. Par exemple, si vous voulez prévoir les informations d'un utilisateur en utilisant l'endpoint `/predict`, votre requête POST pourrait être la suivante :

```bash
curl -X POST 'http://localhost:8000/predict' \
  -H 'Authorization: Bearer YOUR_ACCESS_TOKEN' \
  -d '{"first_name": "John", "last_name": "Doe", "email": "john.doe@example.com", "age": 30, "sex": "Male", "favorite_color": "Red", "favorite_food": "Pizza"}'
```

Lorsque vous aurez obtenu le résultat de la prévision, vous pouvez l'utiliser pour prendre des décisions éclairées.

**Note**
Il est important de noter que cet exemple d'API n'est pas sécurisé et devrait être considéré comme une simple démonstration. Dans une application réelle, il est essentiel de mettre en place un mécanisme d'autorisation plus robuste et de chiffrer les données utilisateur pour garantir leur sécurité.