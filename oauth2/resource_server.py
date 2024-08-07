# resource_server.py
class ResourceServer:
    def __init__(self):
        self.user_data = {
            "alice": "Données confidentielles d'Alice",
            "bob": "Données confidentielles de Bob"
        }

    def get_user_data(self, username):
        return self.user_data.get(username, "Utilisateur non trouvé")