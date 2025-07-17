from passlib.context import CryptContext

pwd_context = CryptContext(
    schemes=['argon2'],
    deprecated="auto"
)


def hashed_password(password: str):
    return pwd_context.hash(password)


def verify_password(plain_password:str, hashed_password) -> bool:
    return pwd_context.verify(plain_password, hashed_password)