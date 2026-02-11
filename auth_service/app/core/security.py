import bcrypt
import hashlib


def hash_secret(secret: str) -> str:
    salt = bcrypt.gensalt()
    secret_bytes = hashlib.sha256(secret.encode()).digest()
    hashed_secret = bcrypt.hashpw(secret_bytes, salt)
    return hashed_secret.decode()


def verify_secret(secret: str, hashed: str) -> bool:
    return bcrypt.checkpw(hashlib.sha256(secret.encode()).digest(), hashed.encode())
