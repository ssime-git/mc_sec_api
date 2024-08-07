# client.py
import requests

class Client:
    def __init__(self, api_base_url):
        self.api_base_url = api_base_url
        self.client_id = "myclient"
        self.client_secret = "mysecret"

    def start_oauth_flow(self, username):
        # Étape 1 : Obtenir le code d'autorisation
        auth_code_response = requests.post(f"{self.api_base_url}/auth", json={"client_id": self.client_id, "username": username})
        auth_code = auth_code_response.json()["auth_code"]
        print(f"Code d'autorisation obtenu : {auth_code}")

        # Étape 2 : Échanger le code d'autorisation contre un jeton d'accès
        token_response = requests.post(f"{self.api_base_url}/token", json={"client_id": self.client_id, "client_secret": self.client_secret, "auth_code": auth_code})
        access_token = token_response.json()["access_token"]
        print(f"Jeton d'accès obtenu : {access_token}")

        # Étape 3 : Utiliser le jeton d'accès pour obtenir des ressources
        data_response = requests.get(f"{self.api_base_url}/data", headers={"Authorization": f"Bearer {access_token}"})
        user_data = data_response.json()["data"]
        print(f"Données de l'utilisateur : {user_data}")

# Utilisation
if __name__ == "__main__":
    client = Client("http://0.0.0.0:5000")
    client.start_oauth_flow("alice")