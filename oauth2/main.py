# main.py
from api import app
from client import Client
import threading
import time

if __name__ == "__main__":
    # Démarrer le serveur Flask dans un thread séparé
    server_thread = threading.Thread(target=app.run, kwargs={"debug": False, "port": 5000, "host": "0.0.0.0"})
    server_thread.start()

    # Attendre que le serveur démarre
    time.sleep(2)

    # Utiliser le client pour tester le flux OAuth2
    client = Client("http://localhost:5000")
    client.start_oauth_flow("alice")