import urllib.parse

from ..config import SESSION_COOKIE, SESSION_TTL_SECONDS
from ..services.auth_service import handle_google_auth
from ..services.google_oauth_service import (
    build_auth_url,
    exchange_code_for_userinfo,
    is_google_configured,
    parse_state,
)
from ..services.session_service import create_session, delete_session
from ..utils.http_utils import (
    build_clear_cookie,
    build_session_cookie,
    get_cookie,
    query_params,
    redirect,
    send_json,
)


def auth_session(handler, current_user):
    if not current_user:
        return send_json(handler, 200, {"authenticated": False, "user": None})
    return send_json(
        handler,
        200,
        {
            "authenticated": True,
            "user": {
                "id": current_user["id"],
                "email": current_user["email"],
                "name": current_user["name"],
                "role": current_user["role"],
            },
        },
    )


def auth_logout(handler):
    token = get_cookie(handler, SESSION_COOKIE)
    delete_session(token)
    handler.send_response(200)
    handler.send_header("Set-Cookie", build_clear_cookie(SESSION_COOKIE))
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.end_headers()
    handler.wfile.write(b'{"ok": true}')


def google_start(handler):
    if not is_google_configured():
        return send_json(handler, 500, {"error": "google_not_configured"})

    params = query_params(handler.path)
    mode = (params.get("mode") or [""])[0]
    role = (params.get("role") or [""])[0]
    if mode not in ("login", "signup") or role not in ("student", "parent"):
        return send_json(handler, 400, {"error": "invalid_mode_or_role"})

    redirect(handler, build_auth_url(mode, role))


def google_callback(handler):
    try:
        params = query_params(handler.path)
        code = (params.get("code") or [""])[0]
        state = (params.get("state") or [""])[0]
        if not code or not state:
            return redirect(handler, "/auth/login.html?error=invalid_callback")

        mode, role = parse_state(state)
        if not mode or not role:
            return redirect(handler, "/auth/login.html?error=invalid_state")

        identity = exchange_code_for_userinfo(code)
        user, error = handle_google_auth(
            email=identity["email"],
            name=identity["name"],
            role=role,
            mode=mode,
        )
        if error == "account_not_exist":
            msg = urllib.parse.quote("Account does not exist")
            return redirect(handler, f"/auth/login.html?role={role}&error={msg}")
        if error == "account_already_exists":
            msg = urllib.parse.quote("Account already exists")
            return redirect(handler, f"/auth/signup.html?role={role}&error={msg}")
        if error:
            return redirect(handler, "/auth/login.html?error=authentication_failed")

        session_token = create_session(user["id"])
        handler.send_response(302)
        handler.send_header("Set-Cookie", build_session_cookie(SESSION_COOKIE, session_token, SESSION_TTL_SECONDS))
        handler.send_header("Location", "/")
        handler.end_headers()
    except Exception:
        redirect(handler, "/auth/login.html?error=google_auth_failed")
