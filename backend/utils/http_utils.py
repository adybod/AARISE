import json
from http import cookies
from urllib.parse import parse_qs, urlparse


def parse_json_body(handler):
    length = int(handler.headers.get("Content-Length", "0"))
    if length <= 0:
        return {}
    raw = handler.rfile.read(length).decode("utf-8")
    return json.loads(raw) if raw else {}


def send_json(handler, status, payload):
    body = json.dumps(payload).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def redirect(handler, location, headers=None):
    handler.send_response(302)
    if headers:
        for key, value in headers:
            handler.send_header(key, value)
    handler.send_header("Location", location)
    handler.end_headers()


def query_params(path):
    return parse_qs(urlparse(path).query)


def get_cookie(handler, name):
    cookie_header = handler.headers.get("Cookie")
    if not cookie_header:
        return None
    jar = cookies.SimpleCookie()
    jar.load(cookie_header)
    morsel = jar.get(name)
    return morsel.value if morsel else None


def build_session_cookie(name, value, max_age):
    return f"{name}={value}; Path=/; HttpOnly; SameSite=Lax; Max-Age={max_age}"


def build_clear_cookie(name):
    return f"{name}=; Path=/; HttpOnly; SameSite=Lax; Max-Age=0"
