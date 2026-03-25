# users.py

# Simple user store (can later be DB / hashed passwords)
USERS = {
    "admin": {
        "password": "1234",
        "role": "admin"
    },
    "operator": {
        "password": "operator123",
        "role": "operator"
    }
}

def authenticate(username: str, password: str):
    """
    Returns user dict if valid, else None
    """
    user = USERS.get(username)
    if not user:
        return None

    if user["password"] != password:
        return None

    return {
        "username": username,
        "role": user["role"]
    }
