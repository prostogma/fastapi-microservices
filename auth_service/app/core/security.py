import bcrypt


def hash_secret(secret: str) -> str:
    salt = bcrypt.gensalt()
    secret_bytes: bytes = secret.encode()
    hashed_secret = bcrypt.hashpw(secret_bytes, salt)
    return hashed_secret.decode()


def verify_secret(secret: str, hashed: str) -> bool:
    return bcrypt.checkpw(secret.encode(), hashed.encode())
