# api.py
from flask import Flask, request, jsonify
from auth_server import AuthorizationServer
from resource_server import ResourceServer

app = Flask(__name__)
auth_server = AuthorizationServer()
resource_server = ResourceServer()

@app.route("/auth", methods=["POST"])
def authorize():
    data = request.json
    auth_code = auth_server.generate_auth_code(data["client_id"], data["username"])
    return jsonify({"auth_code": auth_code})

@app.route("/token", methods=["POST"])
def token():
    data = request.json
    access_token = auth_server.exchange_auth_code_for_token(data["auth_code"], data["client_id"], data["client_secret"])
    if access_token:
        return jsonify({"access_token": access_token})
    return jsonify({"error": "Invalid auth code"}), 400

@app.route("/data", methods=["GET"])
def get_data():
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        username = auth_server.validate_token(token)
        if username:
            data = resource_server.get_user_data(username)
            return jsonify({"data": data})
    return jsonify({"error": "Unauthorized"}), 401