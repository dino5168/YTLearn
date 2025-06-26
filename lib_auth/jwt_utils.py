import jwt
from datetime import datetime, timedelta

JWT_SECRET = "your_jwt_secret"  # 實際上從環境變數讀取


def create_jwt(data: dict, expires_minutes=60):
    payload = {
        **data,
        "exp": datetime.utcnow() + timedelta(minutes=expires_minutes),
        "iat": datetime.utcnow(),
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
