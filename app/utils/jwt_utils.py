# app/utils/jwt_utils.py

from datetime import datetime, timedelta
from functools import wraps

import jwt
from flask import request, jsonify, g

from ..config import JWT_SECRET, JWT_EXPIRES_MINUTES
from ..models import User


def create_token(user: User) -> str:
    """
    יוצר JWT עבור משתמש.
    השדות העיקריים:
    - sub: מזהה המשתמש
    - email: מייל
    - exp: מתי הטוקן פג תוקף
    """
    now = datetime.utcnow()
    payload = {
        "sub": user.id,
        "email": user.email,
        "iat": now,
        "exp": now + timedelta(minutes=JWT_EXPIRES_MINUTES),
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
    # ב-PyJWT 2.x זה כבר מחזיר str
    return token


def decode_token(token: str):
    """
    מנסה לפענח JWT.
    במקרה של שגיאה – זורק Exception של jwt.
    """
    return jwt.decode(token, JWT_SECRET, algorithms=["HS256"])


def get_token_from_request() -> str | None:
    """
    מחפש טוקן ב:
    - Authorization: Bearer <token>
    - או בקוקי בשם access_token (אם נרצה בעתיד)
    """
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        return auth_header.split(" ", 1)[1].strip()

    cookie_token = request.cookies.get("access_token")
    if cookie_token:
        return cookie_token

    return None


def require_auth(fn):
    """
    דקורטור לפעולות שמחייבות משתמש מחובר.
    - בודק שיש טוקן
    - מפענח אותו
    - מוצא את המשתמש בבסיס הנתונים
    - שם אותו ב-g.current_user
    - אם משהו נכשל → 401
    """

    @wraps(fn)
    def wrapper(*args, **kwargs):
        token = get_token_from_request()
        if not token:
            return jsonify({"error": "Missing or invalid auth token"}), 401

        try:
            payload = decode_token(token)
            user_id = payload.get("sub")
            user = User.query.get(user_id)
            if not user:
                return jsonify({"error": "User not found"}), 401

            # נגיש בתוך ה-request
            g.current_user = user

        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401

        return fn(*args, **kwargs)

    return wrapper
