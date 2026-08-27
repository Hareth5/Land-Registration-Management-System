from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, Request
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"])


def hash_password(passwords: str):
    return pwd_context.hash(passwords)


def verify_password(password: str, hash_password: str):
    return pwd_context.verify(password, hash_password)


def create_token(data: dict, expires_delta: timedelta):
    if settings.SECRET_KEY is None:
        raise RuntimeError("SECRET_KEY must be configured before creating tokens")

    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    encode_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY.get_secret_value(),
        algorithm=settings.ALGORITHM,
    )
    return encode_jwt


def verify_token(token: str):
    if settings.SECRET_KEY is None:
        return None

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY.get_secret_value(),
            algorithms=[settings.ALGORITHM],
        )
        email = payload.get("sub")
        if email is None:
            raise JWTError
        return email
    except JWTError:
        return None


def get_current_user(request: Request):
    access_token = request.cookies.get("access_token")
    if access_token is None:
        raise HTTPException(status_code=401, detail="Token missing")
    email = verify_token(access_token)
    if email is None:
        raise HTTPException(status_code=401, detail="Invalid Token")
    return email
