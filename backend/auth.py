from flask import Blueprint, request, jsonify, session, send_from_directory
from users import authenticate

auth = Blueprint("auth", __name__)

@auth.route("/login", methods=["GET"])
def login_page():
    return send_from_directory("frontend", "login.html")

@auth.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "Expected JSON"}), 400

    username = data.get("username")
    password = data.get("password")

    user = authenticate(username, password)

    if not user:
        return jsonify({"success": False}), 401

    session.clear()
    session["user"] = user["username"]
    session["role"] = user["role"]

    return jsonify({"success": True})

@auth.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"success": True})
