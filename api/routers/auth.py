from fastapi import APIRouter, HTTPException, Depends, Request, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from google.oauth2 import id_token as google_id_token
from google.auth.transport import requests as google_requests
import os
from datetime import datetime, timedelta
import jwt
import requests

from lib_auth.jwt_utils import create_jwt

# User
from lib_db.schemas.User import UserRead  # Pydantic Schema
from lib_db.models.User import User
from lib_db.db.get_db import get_db
from pydantic import BaseModel
from urllib.parse import urlencode

# 環境變數配置
GOOGLE_CLIENT_ID = os.getenv(
    "GOOGLE_CLIENT_ID",
    "440121911282-n1tkv3rtrfu9vnm63ajsrm709vc00h3l.apps.googleusercontent.com",
)
GOOGLE_CLIENT_SECRET = os.getenv(
    "GOOGLE_CLIENT_SECRET", "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"
)
JWT_SECRET = "your-jwt-secret"  # os.getenv("JWT_SECRET", "your-jwt-secret")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_HOURS = 24
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

auth_router = APIRouter(prefix="/auth", tags=["auth"])


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


def create_access_token(data: dict, expires_delta: timedelta = None):
    print("create_access_token01")
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(hours=JWT_EXPIRE_HOURS))
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    print("create_access_token02")
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    print("create_access_token03")
    return encoded_jwt


@auth_router.get("/google")
def get_google_auth_url():
    """取得 Google OAuth 授權 URL"""
    print("取得 Google OAuth 授權 URL")
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": "http://127.0.0.1:8000/auth/google/callback",
        "scope": "openid email profile",
        "response_type": "code",
        "access_type": "offline",
        "prompt": "consent",
    }
    auth_url = f"https://accounts.google.com/o/oauth2/auth?{urlencode(params)}"
    return {"auth_url": auth_url}


@auth_router.get("/google/callback")
def google_callback(request: Request, db: Session = Depends(get_db)):
    """處理 Google OAuth 回調"""
    print("處理 Google OAuth 回調")
    code = request.query_params.get("code")
    error = request.query_params.get("error")

    if error:
        print("login error")
        return RedirectResponse(f"{FRONTEND_URL}/login?error={error}")

    if not code:
        print("Authorization code not provided")
        raise HTTPException(status_code=400, detail="Authorization code not provided")

    try:
        # 交換授權碼為 access token 與 id_token
        print("交換授權碼為 access token 與 id_token")
        token_resp = requests.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": code,
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "redirect_uri": "http://127.0.0.1:8000/auth/google/callback",
                "grant_type": "authorization_code",
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        token_resp.raise_for_status()
        token_json = token_resp.json()
        print("=================")
        print("Token response JSON:", token_json)

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

        name = idinfo.get("name", "")
        avatar_url = idinfo.get("picture", "")
        google_id = idinfo.get("sub")

        # 查詢或建立使用者
        print("查詢或建立使用者")
        user = db.query(User).filter(User.email == email).first()
        if not user:
            user = User(
                email=email,
                name=name,
                google_id=google_id,
                avatar_url=avatar_url,
                is_active=True,
                created_at=datetime.utcnow(),
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        else:
            user.name = name
            user.avatar_url = avatar_url
            user.google_id = google_id
            user.last_login = datetime.utcnow()
            db.commit()

        # 產生 JWT
        print("產生 JWT")
        print(f"${user.id} {user.email,user.name}")
        token_data = {
            "user_id": user.id,
            "email": user.email,
            "name": user.name,
            "sub": str(user.id),
        }
        jwt_token = create_access_token(data=token_data)
        print("導回前端，帶上 JWT Token")
        # 導回前端，帶上 JWT Token
        return RedirectResponse(f"http://localhost:3000/auth/success?token={jwt_token}")
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


@auth_router.post("/verify")
def verify_token(request: Request):
    """驗證 JWT token"""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")

    token = auth_header.split(" ")[1]

    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return {"valid": True, "payload": payload}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


@auth_router.post("/logout")
def logout():
    """登出（前端需要清除 token）"""
    return {"message": "Logged out successfully"}
