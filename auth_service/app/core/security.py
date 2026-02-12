import bcrypt
import hashlib


# Хеширование пароля с помощью bcrypt
def hash_secret(secret: str) -> str:
    salt = bcrypt.gensalt()
    secret_bytes: bytes = secret.encode()
    hashed_secret = bcrypt.hashpw(secret_bytes, salt)
    return hashed_secret.decode()


def verify_secret(secret: str, hashed: str) -> bool:
    return bcrypt.checkpw(secret.encode(), hashed.encode())


# Хеширование с помощью sha256
def hash_refresh_token(secret: str) -> str:
    return hashlib.sha256(secret.encode()).hexdigest()


def verify_refresh_token(raw_token: str, stored_hash: str) -> bool:
    computed_hash = hashlib.sha256(raw_token.encode()).hexdigest()
    return computed_hash == stored_hash
