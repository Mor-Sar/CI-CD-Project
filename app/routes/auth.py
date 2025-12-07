# app/routes/auth.py

import os
import jwt
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from ..models import User
from .. import db



# Blueprint לאנדפוינטים של Auth
auth_bp = Blueprint("auth", __name__)

# המפתח לחתימה על ה-JWT
# אם יש בקובץ .env משתנה JWT_SECRET הוא ישתמש בו, אחרת ברירת מחדל (לפיתוח)
JWT_SECRET = os.getenv("JWT_SECRET", "dev-super-secret-change-me")
JWT_ALGORITHM = "HS256"


def create_token(user_id: int) -> str:
    """
    יוצר JWT שכולל:
    - user_id: מזהה המשתמש
    - exp: תאריך תפוגה (עוד 6 שעות)
    """
    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(hours=6),
    }

    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    # בחלק מהגרסאות זה מחזיר bytes, אז נהפוך ל-str
    if isinstance(token, bytes):
        token = token.decode("utf-8")

    return token


def get_token_from_header():
    """
    מוציא את הטוקן מה-Authorization header.
    מצפה לפורמט:  Authorization: Bearer <token>
    """
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        return auth_header[7:]
    return auth_header or None


@auth_bp.route("/auth/register", methods=["POST"])
def register():
    data = request.get_json() or {}

    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    # basic validation
    if not username or not email or not password:
        return jsonify({"error": "username, email and password are required"}), 400

    # check if email already exists
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "email already exists"}), 400

    # check if username already exists
    if User.query.filter_by(username=username).first():
        return jsonify({"error": "username already exists"}), 400

    # create user
    user = User(username=username, email=email)
    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "registered successfully", "user": user.to_dict()}), 201


@auth_bp.route("/auth/login", methods=["POST"])
def login():
    """
    התחברות.
    מצפה ל-JSON:
    {
        "email": "test@example.com",
        "password": "123456"
    }
    מחזיר:
    {
        "token": "...",
        "user": {...}
    }
    """
    data = request.get_json() or {}

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "email and password are required"}), 400

    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(password):
        return jsonify({"error": "invalid credentials"}), 401

    token = create_token(user.id)

    return jsonify({"token": token, "user": user.to_dict()}), 200


@auth_bp.route("/auth/me", methods=["GET"])
def me():
    """
    מחזיר את פרטי המשתמש הנוכחי לפי הטוקן.
    צריך לשלוח Header:
    Authorization: Bearer <token>
    """
    token = get_token_from_header()

    if not token:
        return jsonify({"error": "missing token"}), 401

    try:
        data = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "token expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "invalid token"}), 401

    user = User.query.get(data["user_id"])
    if not user:
        return jsonify({"error": "user not found"}), 404

    return jsonify(user.to_dict()), 200
