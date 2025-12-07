# app/utils/auth_utils.py

import jwt
from flask import request, jsonify
from functools import wraps
from ..models import User

SECRET = "supersecretkey"   # אותו מפתח מה-auth.py


def get_current_user():
    token = request.headers.get("Authorization")

    if not token:
        return None

    try:
        data = jwt.decode(token, SECRET, algorithms=["HS256"])
        user = User.query.get(data["user_id"])
        return user
    except Exception:
        return None


def require_user(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        user = get_current_user()
        if not user:
            return jsonify({"error": "auth required"}), 401
        # מעבירים את המשתמש לפונקציה כפרמטר ראשון
        return f(user, *args, **kwargs)

    return wrapper
