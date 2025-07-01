import jwt
from datetime import datetime, timedelta

from api.config import settings

JWT_SECRET = settings.JWT_SECRET_KEY  # 實際上從環境變數讀取


def create_jwt(data: dict, expires_minutes=60):
    payload = {
        **data,
        "exp": datetime.now() + timedelta(minutes=expires_minutes),
        "iat": datetime.now(),
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
    return token


def decode_jwt(token: str):
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
