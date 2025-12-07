# app/routes/core.py
from flask import Blueprint, render_template

core_bp = Blueprint("core", __name__)

@core_bp.route("/")
def index():
    return render_template("index.html")

@core_bp.route("/login")
def login_page():
    return render_template("login.html")

@core_bp.route("/register")
def register_page():
    return render_template("register.html")
