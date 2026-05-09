from ..middleware.auth_middleware import require_user
from ..models.activity_repo import add_activity, list_activities
from ..models.profile_repo import get_profile, update_profile
from ..utils.http_utils import parse_json_body, send_json


def get_me(handler):
    user = require_user(handler)
    if not user:
        return send_json(handler, 401, {"error": "unauthorized"})
    return send_json(
        handler,
        200,
        {
            "id": user["id"],
            "email": user["email"],
            "name": user["name"],
            "role": user["role"],
        },
    )


def get_profile_route(handler):
    user = require_user(handler)
    if not user:
        return send_json(handler, 401, {"error": "unauthorized"})
    profile = get_profile(user["id"])
    return send_json(handler, 200, profile)


def update_profile_route(handler):
    user = require_user(handler)
    if not user:
        return send_json(handler, 401, {"error": "unauthorized"})
    body = parse_json_body(handler)
    update_profile(
        user["id"],
        (body.get("grade") or "").strip(),
        (body.get("targets") or "").strip(),
        (body.get("goal") or "").strip(),
    )
    return send_json(handler, 200, {"ok": True})


def list_activities_route(handler):
    user = require_user(handler)
    if not user:
        return send_json(handler, 401, {"error": "unauthorized"})
    return send_json(handler, 200, {"items": list_activities(user["id"])})


def create_activity_route(handler):
    user = require_user(handler)
    if not user:
        return send_json(handler, 401, {"error": "unauthorized"})
    body = parse_json_body(handler)
    content = (body.get("content") or "").strip()
    if not content:
        return send_json(handler, 400, {"error": "content_required"})
    add_activity(user["id"], content)
    return send_json(handler, 200, {"ok": True})
