import secrets


def generate_refresh_token() -> str:
    token = secrets.token_urlsafe(32)
    return token

