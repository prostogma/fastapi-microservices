from typing import Annotated
import jwt
from jwt import InvalidTokenError
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.config import settings

http_bearer = HTTPBearer()


def decode_jwt(
    token: str,
    public_key: str = settings.auth_jwt.public_key_path.read_text(),
    algorithm: str = settings.auth_jwt.algorithm,
) -> dict:
    decoded = jwt.decode(jwt=token, key=public_key, algorithms=algorithm)
    return decoded


def verify_jwt(token: str) -> dict:
    try:
        payload = decode_jwt(token)
        return payload
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(http_bearer)],
) -> dict:
    token = credentials.credentials
    payload = verify_jwt(token)

    return payload


def require_verified_user(user: Annotated[dict, Depends(get_current_user)]) -> dict:
    if not user.get("is_verified"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Email not verified!"
        )

    return user
