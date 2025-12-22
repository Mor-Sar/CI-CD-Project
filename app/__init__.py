# app/__init__.py

from flask import Flask, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

from .config import (
    SQLALCHEMY_DATABASE_URI,
    SQLALCHEMY_TRACK_MODIFICATIONS,
)

db = SQLAlchemy()


def create_app():
    app = Flask(
        __name__,
        static_folder="static",      # קבצי CSS / JS
        template_folder="templates"  # קבצי HTML
    )

    # הגדרות DB
    app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = SQLALCHEMY_TRACK_MODIFICATIONS

    # חיבור ה-DB
    db.init_app(app)

    # טעינת המודלים כדי ש-SQLAlchemy יכיר אותם
    from . import models  # noqa: F401

    # ייבוא ה-Blueprints של ה-API
    from .routes.topics import topics_bp
    from .routes.cards import cards_bp
    from .routes.auth import auth_bp

    app.register_blueprint(topics_bp)
    app.register_blueprint(cards_bp)
    app.register_blueprint(auth_bp)

    # --------- ROUTES לדפים ---------

    @app.route("/", methods=["GET"])
    def index():
        """דף האפליקציה הראשי (רק אחרי התחברות)."""
        return render_template("index.html")

    @app.route("/login", methods=["GET"])
    def login_page():
        """דף התחברות."""
        return render_template("login.html")

    @app.route("/register", methods=["GET"])
    def register_page():
        """דף הרשמה."""
        return render_template("register.html")

    @app.route("/health", methods=["GET"])
    def health():
        try:
            db.session.execute(text("SELECT 1"))
            return jsonify({"status": "ok", "db": "ok"}), 200
        except Exception as e:
            return jsonify({"status": "error", "db": "down", "message": str(e)}), 503


    # יצירת טבלאות אם לא קיימות
    with app.app_context():
        db.create_all()

    return app
