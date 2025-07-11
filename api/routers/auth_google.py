from fastapi import APIRouter, HTTPException, Depends, Request, Query
from fastapi.responses import RedirectResponse, Response
from sqlalchemy.orm import Session
from google.oauth2 import id_token as google_id_token
from google.auth.transport import requests as google_requests
import os
from datetime import datetime, timedelta, timezone
import jwt
import requests

# from lib_auth.jwt_utils import create_jwt

# User
# from lib_db.schemas.User import UserRead  # Pydantic Schema
from lib_db.models.User import User
from lib_db.db.database import get_db
from pydantic import BaseModel
from urllib.parse import urlencode
from app.config import settings

# 環境變數配置
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", settings.GOOGLE_CLIENT_ID)
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", settings.GOOGLE_CLIENT_SECRET)

JWT_SECRET = settings.JWT_SECRET_KEY  # os.getenv("JWT_SECRET", "your-jwt-secret")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_HOURS = 24
FRONTEND_URL = settings.FRONTEND_URL
GOOGLE_CALL_BACK_URL = settings.GOOGLE_CALL_BACK_URL
GOOGLE_REDIRECT_URL = settings.GOOGLE_REDIRECT_URL
GOOGLE_TOKEN_URL = settings.GOOGLE_TOKEN_URL
FRONTEDN_GOOGLE_SUCCESS = settings.FRONTEDN_GOOGLE_SUCCESS
ADMIN_EMAIL = settings.ADMIN_EMAIL = settings.ADMIN_EMAIL

auth_google = APIRouter(prefix="/auth", tags=["auth"])


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


# 取得 jwt token
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    expire = now + (expires_delta or timedelta(hours=JWT_EXPIRE_HOURS))

    # 更保守的時間設定
    to_encode.update(
        {
            "exp": expire,
            "iat": now,
            "nbf": now - timedelta(seconds=10),  # 增加到 10 秒緩衝
        }
    )

    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt


@auth_google.get("/google")
def get_google_auth_url():
    """取得 Google OAuth 授權 URL"""
    # print("取得 Google OAuth 授權 URL")
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": GOOGLE_CALL_BACK_URL,
        "scope": "openid email profile",
        "response_type": "code",
        "access_type": "offline",
        "prompt": "consent",
    }
    # 跳轉到 Google 的登入與授權頁面
    auth_url = f"{GOOGLE_REDIRECT_URL}?{urlencode(params)}"
    return {"auth_url": auth_url}


@auth_google.get("/google/callback")
def google_callback(request: Request, db: Session = Depends(get_db)):
    """處理 Google OAuth 回調"""
    print("處理 Google OAuth 回調")
    code = request.query_params.get("code")
    error = request.query_params.get("error")
    # 如果有錯誤，則返回錯誤訊息 ; 使用者取消授權

    if error:
        print("login error")
        return RedirectResponse(f"{FRONTEND_URL}/")

    if not code:
        print("Authorization code not provided")
        raise HTTPException(status_code=400, detail="Authorization code not provided")

    try:
        # 交換授權碼為 access token 與 id_token
        print("交換授權碼為 access token 與 id_token")
        token_resp = requests.post(
            GOOGLE_TOKEN_URL,
            data={
                "code": code,
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "redirect_uri": GOOGLE_CALL_BACK_URL,
                "grant_type": "authorization_code",
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        token_resp.raise_for_status()
        token_json = token_resp.json()
        # print("=================")
        # print("Token response JSON:", token_json)

        id_token_str = token_json.get("id_token")
        if not id_token_str:
            raise HTTPException(status_code=400, detail="No id_token in token response")

        # 驗證 id_token
        idinfo = google_id_token.verify_oauth2_token(
            id_token_str, google_requests.Request(), GOOGLE_CLIENT_ID
        )

        # 讀取使用者資訊
        email = idinfo.get("email")

        if not email:
            raise HTTPException(status_code=400, detail="No email in token")

        #google email 是否認證
        email_verified = idinfo.get("email_verified")
        # email 是否認證
        if not email_verified:
            raise HTTPException(status_code=400, detail="Email not verified")

        default_role_id = 6  # 預設角色 ID，根據實際情況調整
        if email == ADMIN_EMAIL:
            default_role_id = 1

        name = idinfo.get("name", "")
        avatar_url = idinfo.get("picture", "")
        google_id = idinfo.get("sub")

        # 查詢或建立使用者
        # print("查詢或建立使用者")
        user = db.query(User).filter(User.email == email).first()
        if not user:
            user = User(
                email=email,
                name=name,
                google_id=google_id,
                avatar_url=avatar_url,
                is_active=True,
                role_id=default_role_id,  # 預設角色 ID，根據實際情況調整
                created_at=datetime.now(),
                last_login_at=datetime.now(),
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        else:
            user.name = name
            user.avatar_url = avatar_url
            user.google_id = google_id
            user.last_login_at = datetime.now()
            db.commit()

        # 產生 JWT
        # print("產生 JWT")
        # print(f"user:id = {user.id} , {user.email,user.name} , role_id: {user.role_id}")
        token_data = {
            "user_id": user.id,
            "email": user.email,
            "name": user.name,
            "avatar_url": avatar_url,
            "sub": str(user.id),
            "role_id": user.role_id,
        }

        jwt_token = create_access_token(data=token_data)
        # print("導回前端，帶上 JWT Token")
        # 導回前端，帶上 JWT Token
        return RedirectResponse(f"{FRONTEDN_GOOGLE_SUCCESS}?token={jwt_token}")
        # print("導回前端，帶上 JWT Token")
        # return RedirectResponse(f"http:/127.0.0.1:3000")

    except requests.HTTPError as e:
        print("erorr 01")
        raise HTTPException(
            status_code=400, detail=f"Failed to exchange code for token: {str(e)}"
        )
    except Exception as e:
        print("erorr 02")
        raise HTTPException(status_code=500, detail=f"Authentication failed: {str(e)}")


@auth_google.post("/verify")
def verify_token(request: Request):
    """驗證 JWT token"""
    print("驗證 JWT token")
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")

    token = auth_header.split(" ")[1]
    # 回傳前端 jwt token 放在 payload
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return {"valid": True, "payload": payload}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


@auth_google.post("/logout")
def logout(response: Response):
    """登出（前端需要清除 token）"""
    """
    登出 - 從後端角度來說，告訴前端要清除 token。
    也可以直接清除 httpOnly cookie (如果你是用 cookie 存 token)。
    """
    # 如果你是用 httpOnly cookie 存 token，可以這樣清除 cookie：
    response.delete_cookie(key="auth_token")
    return {"message": "Logged out successfully"}
