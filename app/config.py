
# app/config.py
import os
from dotenv import load_dotenv

# -----------------------------
# Paths
# -----------------------------
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
ENV_PATH = os.path.join(BASE_DIR, ".env")

# -----------------------------
# Environment (local | ci | prod)
# -----------------------------
APP_ENV = os.getenv("APP_ENV", "local").strip().lower()

# Load .env only in local (each developer has their own .env; never commit it)
if APP_ENV == "local" and os.path.exists(ENV_PATH):
    load_dotenv(ENV_PATH)

def require(name: str) -> str:
    """Require an environment variable (no defaults)."""
    value = os.getenv(name)
    if value is None or value.strip() == "":
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value

# -----------------------------
# Database (MariaDB / MySQL) - NO DEFAULTS
# -----------------------------
MYSQL_DB = require("MYSQL_DB")
MYSQL_USER = require("MYSQL_USER")
MYSQL_PASSWORD = require("MYSQL_PASSWORD")
MYSQL_HOST = require("MYSQL_HOST")  # docker-compose service name (usually "mariadb")
MYSQL_PORT = require("MYSQL_PORT")  # usually "3306"

SQLALCHEMY_DATABASE_URI = (
    f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}"
    f"@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
)
SQLALCHEMY_TRACK_MODIFICATIONS = False

# -----------------------------
# JWT / Auth - NO DEFAULTS
# -----------------------------
JWT_SECRET = require("JWT_SECRET")
JWT_EXPIRES_MINUTES = int(require("JWT_EXPIRES_MINUTES"))

# -----------------------------
# AI - Gemini only (NO DEFAULTS)
# -----------------------------
AI_PROVIDER = require("AI_PROVIDER").strip().lower()  # must be "gemini"
if AI_PROVIDER != "gemini":
    raise RuntimeError("AI_PROVIDER must be 'gemini' for this project")

GEMINI_API_KEY = require("GEMINI_API_KEY")
GEMINI_MODEL = require("GEMINI_MODEL")
AI_ENABLED = True

# -----------------------------
# OpenAI (kept for backward compatibility, not used)
# -----------------------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "")

