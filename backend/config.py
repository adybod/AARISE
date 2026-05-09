import os


BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "aarise.db")
PUBLIC_DIR = os.path.join(BASE_DIR, "public")

HOST = os.getenv("AARISE_HOST", "127.0.0.1")
PORT = int(os.getenv("AARISE_PORT", "8000"))

SESSION_COOKIE = "aarise_session"
SESSION_TTL_SECONDS = 60 * 60 * 24 * 30

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", f"http://{HOST}:{PORT}/api/auth/google/callback")
