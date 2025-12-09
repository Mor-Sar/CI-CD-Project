# app/utils/auth_utils.py

import jwt
from flask import request, jsonify
from functools import wraps

from ..models import User
from ..config import JWT_SECRET  # משתמשים באותו מפתח כמו ב-auth.py

JWT_ALGORITHM = "HS256"


def _extract_token_from_header():
    """
    מוציא את הטוקן מה-Authorization header.

    תומך גם ב:
    - "Authorization: Bearer <token>"
    - "Authorization: <token>"
    """
    auth_header = request.headers.get("Authorization", "") or ""

    auth_header = auth_header.strip()
    if not auth_header:
        return None

    if auth_header.startswith("Bearer "):
        return auth_header[len("Bearer ") :].strip()

    return auth_header


def get_current_user():
    token = _extract_token_from_header()
    if not token:
        return None

    try:
        data = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user = User.query.get(data.get("user_id"))
        return user
    except jwt.ExpiredSignatureError:
        # טוקן פג תוקף
        return None
    except jwt.InvalidTokenError:
        # טוקן לא חוקי
        return None
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
