import json
import urllib.parse
import urllib.request
import uuid

from ..config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REDIRECT_URI


GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"


def is_google_configured():
    return bool(GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET and GOOGLE_REDIRECT_URI)


def build_auth_url(mode, role):
    state = f"{mode}:{role}:{uuid.uuid4().hex}"
    query = urllib.parse.urlencode(
        {
            "client_id": GOOGLE_CLIENT_ID,
            "redirect_uri": GOOGLE_REDIRECT_URI,
            "response_type": "code",
            "scope": "openid email profile",
            "state": state,
            "access_type": "offline",
            "prompt": "select_account",
        }
    )
    return f"{GOOGLE_AUTH_URL}?{query}"


def parse_state(state_value):
    try:
        mode, role, _nonce = state_value.split(":")
        if mode not in ("login", "signup"):
            return None, None
        if role not in ("student", "parent"):
            return None, None
        return mode, role
    except Exception:
        return None, None


def exchange_code_for_userinfo(code):
    token_body = urllib.parse.urlencode(
        {
            "code": code,
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "redirect_uri": GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code",
        }
    ).encode("utf-8")

    token_req = urllib.request.Request(
        GOOGLE_TOKEN_URL,
        data=token_body,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    with urllib.request.urlopen(token_req, timeout=15) as response:
        token_payload = json.loads(response.read().decode("utf-8"))

    access_token = token_payload.get("access_token")
    if not access_token:
        raise ValueError("Missing access token from Google.")

    userinfo_req = urllib.request.Request(
        GOOGLE_USERINFO_URL,
        headers={"Authorization": f"Bearer {access_token}"},
    )
    with urllib.request.urlopen(userinfo_req, timeout=15) as response:
        userinfo = json.loads(response.read().decode("utf-8"))

    email = (userinfo.get("email") or "").strip().lower()
    name = (userinfo.get("name") or "").strip() or "New User"
    if not email:
        raise ValueError("Google account did not return an email.")
    return {"email": email, "name": name}
