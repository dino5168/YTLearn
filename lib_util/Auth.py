# utils/auth.py 或 deps.py

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi import Request
from fastapi.security import OAuth2, OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from lib_db.db.database import get_db
from lib_db.models.User import User
from app.config import settings
import logging

SECRET_KEY = settings.JWT_SECRET_KEY
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/Login")  # 對應你的登入路由


# 設定日誌
logger = logging.getLogger(__name__)


class OptionalOAuth2PasswordBearer(OAuth2PasswordBearer):
    """
    可選的 OAuth2 Bearer token 認證
    當沒有 token 或 token 無效時返回 None，而不是拋出異常
    """

    async def __call__(self, request: Request) -> Optional[str]:
        """
        從請求頭中提取 Bearer token

        Args:
            request: FastAPI 請求對象

        Returns:
            Optional[str]: 提取的 token 或 None
        """
        authorization: Optional[str] = request.headers.get("Authorization")

        # 檢查是否有 Authorization 頭
        if not authorization:
            return None

        # 檢查是否為 Bearer token 格式
        if not authorization.startswith("Bearer "):
            logger.warning(f"Invalid authorization format: {authorization[:20]}...")
            return None

        # 提取 token 部分
        token = authorization[len("Bearer ") :].strip()

        # 檢查 token 是否為空
        if not token:
            logger.warning("Empty token provided")
            return None

        return token


# 實例化可選 OAuth2 認證方案
oauth2_scheme_optional = OptionalOAuth2PasswordBearer(tokenUrl="auth/LoginOptional")


# 依賴注入驗證使用者是否有效
def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> User:
    print("get_current_user")
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="無法驗證身份",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user


# 👤 可選登入：驗證失敗時回傳 None
def get_optional_user(
    token: Optional[str] = Depends(oauth2_scheme_optional),
    db: Session = Depends(get_db),
) -> Optional[User]:
    """
    可選用戶認證依賴

    Args:
        token: 可選的 JWT token
        db: 資料庫會話

    Returns:
        Optional[User]: 認證用戶或 None
    """
    # 如果沒有 token，返回 None
    print("get_optional_user====================================0")
    if token is None:
        return None
    print("get_optional_user====================================1")
    try:
        # 解碼 JWT token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # 提取用戶 ID
        user_id: Optional[int] = payload.get("sub")
        if user_id is None:
            logger.warning("Token payload missing 'sub' claim")
            return None

        # 驗證用戶 ID 類型
        if not isinstance(user_id, int):
            try:
                user_id = int(user_id)
            except (ValueError, TypeError):
                logger.warning(f"Invalid user_id format: {user_id}")
                return None

        # 查詢用戶
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            logger.warning(f"User not found for ID: {user_id}")
            return None

        # 可選：檢查用戶是否啟用
        if hasattr(user, "is_active") and not user.is_active:
            logger.warning(f"User {user_id} is not active")
            return None
        print("get_optional_user====================================")

        return user

    except JWTError as e:
        logger.warning(f"JWT decode error: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error in get_optional_user: {str(e)}")
        return None
