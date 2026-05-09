import json
import mimetypes
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

from .config import HOST, PORT
from .db import init_db
from .middleware.auth_middleware import require_user
from .routes.auth_routes import auth_logout, auth_session, google_callback, google_start
from .routes.user_routes import (
    create_activity_route,
    get_me,
    get_profile_route,
    list_activities_route,
    update_profile_route,
)

ROOT_DIR = os.path.dirname(os.path.dirname(__file__))


def _safe_path(path):
    clean = path.split("?", 1)[0]
    if clean == "/":
        return os.path.join(ROOT_DIR, "website.html")
    candidate = os.path.normpath(os.path.join(ROOT_DIR, clean.lstrip("/")))
    if not candidate.startswith(ROOT_DIR):
        return None
    return candidate


class AppHandler(BaseHTTPRequestHandler):
    def _serve_static(self):
        file_path = _safe_path(self.path)
        if not file_path or not os.path.isfile(file_path):
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not found")
            return
        ctype = mimetypes.guess_type(file_path)[0] or "application/octet-stream"
        with open(file_path, "rb") as f:
            payload = f.read()
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self):
        path = urlparse(self.path).path
        current_user = require_user(self)

        if path == "/api/auth/session":
            return auth_session(self, current_user)
        if path == "/api/auth/google/start":
            return google_start(self)
        if path == "/api/auth/google/callback":
            return google_callback(self)
        if path == "/api/me":
            return get_me(self)
        if path == "/api/me/profile":
            return get_profile_route(self)
        if path == "/api/me/activities":
            return list_activities_route(self)

        return self._serve_static()

    def do_POST(self):
        path = urlparse(self.path).path
        if path == "/api/auth/logout":
            return auth_logout(self)
        if path == "/api/me/activities":
            return create_activity_route(self)
        self.send_response(404)
        self.end_headers()

    def do_PUT(self):
        path = urlparse(self.path).path
        if path == "/api/me/profile":
            return update_profile_route(self)
        self.send_response(404)
        self.end_headers()

    def log_message(self, _fmt, *_args):
        return


def run():
    init_db()
    server = ThreadingHTTPServer((HOST, PORT), AppHandler)
    print(json.dumps({"status": "running", "host": HOST, "port": PORT}))
    server.serve_forever()


if __name__ == "__main__":
    run()
