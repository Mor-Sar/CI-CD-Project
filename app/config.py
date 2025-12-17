# app/config.py
import os
from dotenv import load_dotenv

# בסיס הפרויקט (תיקיית CI-CD-Project)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
ENV_PATH = os.path.join(BASE_DIR, ".env")

if os.path.exists(ENV_PATH):
    load_dotenv(ENV_PATH)

# ---- Database for development ----
#DB_PATH = os.path.join(BASE_DIR, "cards.db")  # או app.db – אצלך כרגע cards.db
#SQLALCHEMY_DATABASE_URI = f"sqlite:///{DB_PATH}"
#SQLALCHEMY_TRACK_MODIFICATIONS = False

# ---- Database (PostgreSQL) ----
POSTGRES_DB = os.getenv("POSTGRES_DB", "flashcards")
POSTGRES_USER = os.getenv("POSTGRES_USER", "flashcards_user")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "flashcards_pass")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "postgres")  # שם ה-service ב-docker-compose
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")

SQLALCHEMY_DATABASE_URI = (
    f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}"
    f"@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
)
SQLALCHEMY_TRACK_MODIFICATIONS = False


# ---- OpenAI ----
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
AI_ENABLED = bool(OPENAI_API_KEY)

# ---- Gemini ----
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
AI_PROVIDER = os.getenv("AI_PROVIDER", "openai")  # "gemini" או "openai"


# ---- JWT / Auth ----
# מפתח חתימה לטוקן (בפרודקשן שמים ערך חזק ב-ENV)
JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-change-me")
# זמן תפוגה של טוקן בדקות
JWT_EXPIRES_MINUTES = int(os.getenv("JWT_EXPIRES_MINUTES", "60"))
