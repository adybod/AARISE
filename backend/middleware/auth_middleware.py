from ..config import SESSION_COOKIE
from ..models.user_repo import get_user_by_id
from ..services.session_service import get_session_user_id
from ..utils.http_utils import get_cookie


def require_user(handler):
    token = get_cookie(handler, SESSION_COOKIE)
    user_id = get_session_user_id(token)
    if not user_id:
        return None
    return get_user_by_id(user_id)
