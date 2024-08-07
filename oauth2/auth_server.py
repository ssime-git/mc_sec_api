# auth_server.py
import random
import string
import time

class AuthorizationServer:
    def __init__(self):
        self.auth_codes = {}
        self.access_tokens = {}

    def generate_auth_code(self, client_id, username):
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        self.auth_codes[code] = {"client_id": client_id, "username": username}
        return code

    def exchange_auth_code_for_token(self, auth_code, client_id, client_secret):
        if auth_code in self.auth_codes and self.auth_codes[auth_code]["client_id"] == client_id:
            username = self.auth_codes[auth_code]["username"]
            del self.auth_codes[auth_code]
            access_token = ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))
            self.access_tokens[access_token] = {"username": username, "expires_at": time.time() + 3600}
            return access_token
        return None

    def validate_token(self, access_token):
        if access_token in self.access_tokens and time.time() < self.access_tokens[access_token]["expires_at"]:
            return self.access_tokens[access_token]["username"]
        return None