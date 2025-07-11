from jose import JWTError, jwt
from datetime import datetime, timedelta
from app.config import settings

SECRET_KEY = settings.JWT_SECRET_KEY  # 實際上從環境變數讀取
# 建議放在 settings
ALGORITHM = "HS256"
EMAIL_TOKEN_EXPIRE_MINUTES = 30  # 驗證信連結有效時間（30分鐘）


def create_email_verification_token(email: str) -> str:
    expire = datetime.now() + timedelta(minutes=EMAIL_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": email, "exp": expire, "type": "email_verify"}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def verify_email_token(token: str) -> str:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "email_verify":
            raise ValueError("Token 類型錯誤")
        return payload.get("sub")  # 回傳 email
    except JWTError as e:
        raise ValueError("無效或過期的 token")
