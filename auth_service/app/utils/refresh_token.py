import secrets


def create_refresh_token() -> str:
    token = secrets.token_urlsafe(64)
    return token
