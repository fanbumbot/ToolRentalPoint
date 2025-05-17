from datetime import datetime, timedelta, timezone

from .consts import *
from .exceptions import *

from jose import jwt, JWTError

def generate_access_token(user_id: int, login: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(days=30)
    payload = {
        "user_id": user_id,
        "login": login,
        "exp": int(expire.timestamp())
    }
    return jwt.encode(payload, TOKEN_SECRET_CODE, algorithm=TOKEN_ALGORITHM)

def decode_token(token: str):
    try:
        data = jwt.decode(token, TOKEN_SECRET_CODE, algorithms=[TOKEN_ALGORITHM])
        return data["user_id"], data["login"], data["exp"]
    except JWTError:
        raise TokenIsInvalidError