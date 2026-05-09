from ..models.user_repo import create_user, get_user_by_email


def handle_google_auth(email, name, role, mode):
    existing = get_user_by_email(email)

    if mode == "login":
        if not existing:
            return None, "account_not_exist"
        return existing, None

    if mode == "signup":
        if existing:
            return None, "account_already_exists"
        return create_user(email=email, name=name, role=role), None

    return None, "invalid_auth_mode"
