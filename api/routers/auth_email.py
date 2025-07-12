import logging
from datetime import datetime

# from pydoc import text

from jose import JWTError, jwt
from sqlalchemy import text

from fastapi import APIRouter, Body, HTTPException, Depends, Request, Query
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.ext.asyncio import AsyncSession
from api.routers.auth_google import create_access_token
from lib_db.db.database import get_async_db

from lib_sql.sql_loader_singleton import get_sql_loader
from lib_sql.SQLQueryExecutor import SQLQueryExecutor
from lib_util.GmailSender import create_email_service
from lib_common.ErrorDetail import ErrorDetail
from lib_auth.user_token import create_email_verification_token, verify_email_token
from passlib.context import CryptContext
from app.config import settings

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

sql_loader = get_sql_loader()

auth_email = APIRouter(prefix="/auth", tags=["auth"])


# 建議使用 Pydantic 模型來定義請求結構
class RegisterRequest(BaseModel):
    email: str = Field(..., description="用戶的 Email 地址")
    password: str = Field(..., description="用戶的密碼", min_length=6, max_length=10)


class RegisterResponse(BaseModel):
    message: str
    success: bool = True


class ForgotPasswordRequest(BaseModel):
    email: EmailStr
    resend: bool = False
    fingerprint: str


# 輔助函數（需要根據實際情況實現）
async def check_email_is_exists(db: AsyncSession, email: str):
    """檢查郵箱是否存在於資料庫中"""
    if not email:
        raise HTTPException(status_code=400, detail="Email is required")
    # 注意：這裡的 "CHECK_USER_EMAIL" 是一個 SQL 查詢語句的名稱，
    # 需要在 SQL 文件中定義這個查詢語句。
    if not db:
        raise HTTPException(status_code=500, detail="Database connection error")
    # 使用 SQLQueryExecutor 執行 SQL 查詢
    executor = SQLQueryExecutor(sql_loader, db)
    result = await executor.execute("CHECK_USER_EMAIL", {"email": email})
    return result


async def send_verification_email(email: str, loginToken: str) -> bool:
    """發送驗證郵件"""
    if not email:
        raise HTTPException(status_code=400, detail="Email is required")
    # 實際實現邏輯
    try:
        email_service = create_email_service()
        result = email_service.send_verification_email(
            email=email, token=loginToken, domain=settings.EMAIL_VERIFY_DOMAIN
        )
        return result.success
    except Exception as e:
        logger.error(f"Error sending verification email: {str(e)}")
        return False


async def send_forgot_email(email: str, loginToken: str) -> bool:
    """發送驗證郵件"""
    if not email:
        raise HTTPException(status_code=400, detail="Email is required")
    # print("send_forget_email")
    try:
        email_service = create_email_service()
        result = email_service.send_password_email(
            email=email, token=loginToken, domain=settings.EMAIL_VERIFY_DOMAIN
        )
        return result.success
    except Exception as e:
        logger.error(f"Error sending verification email: {str(e)}")
        return False


async def update_users_user_token(db: AsyncSession, email: str, token: str) -> None:
    """更新使用者的郵箱驗證狀態"""
    if not email or not token:
        raise HTTPException(status_code=400, detail="Email and token are required")
    # 實際實現邏輯
    executor = SQLQueryExecutor(sql_loader, db)
    result = await executor.execute(
        "UPDATE_USERS_USER_TOKEN", {"email": email, "user_token": token}
    )
    if result is None:
        raise HTTPException(
            status_code=500, detail="Failed to update email verification"
        )


async def update_users_user_password(
    db: AsyncSession, email: str, newPassword: str
) -> None:
    """更新使用者的密碼重設密碼使用"""
    if not email or not newPassword:
        raise HTTPException(
            status_code=400, detail="Email and newPassword are required"
        )
    # 實際實現邏輯
    executor = SQLQueryExecutor(sql_loader, db)
    result = await executor.execute(
        "UPDATE_USERS_USER_PASSWORD", {"email": email, "password_hash": newPassword}
    )
    if result is None:
        raise HTTPException(status_code=500, detail="Failed to update reset password")


# 更新使用者狀態
async def update_users_user_status(db: AsyncSession, email: str, user_status: int):
    executor = SQLQueryExecutor(sql_loader, db)
    result = await executor.execute(
        "UPDATE_USERS_USER_STATUS", {"email": email, "user_status": user_status}
    )
    if result is None:
        raise HTTPException(status_code=500, detail="Failed to bind account to email")


async def bind_account_to_email(db: AsyncSession, email: str, password: str) -> None:
    """將帳號綁定到郵箱"""
    # 實際實現邏輯
    print("bind_account_to_email")
    print(f"Binding account to email: {email} with password hash: {password}")
    executor = SQLQueryExecutor(sql_loader, db)
    result = await executor.execute(
        "UPDATE_USER_EMAIL_VERIFY", {"email": email, "password_hash": password}
    )
    if result is None:
        raise HTTPException(status_code=500, detail="Failed to bind account to email")


# 新增使用者資料
async def create_user(db: AsyncSession, email: str, password: str):
    """創建新用戶"""
    print("create_user")
    print(f"Creating user with email: {email} and password hash: {password}")
    default_role_id = 4
    if email == "dino5168@gmail.com":
        default_role_id = 1
    executor = SQLQueryExecutor(sql_loader, db)
    try:
        # 使用 SQLQueryExecutor 執行 SQL 查詢
        await executor.execute(
            "INSERT_USER_BY_REGISTER",
            {"email": email, "password_hash": password, "role_id": default_role_id},
        )
        return True
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create user")


async def check_user_email_verification_status(db: AsyncSession, email: str) -> bool:
    """檢查用戶郵箱是否已驗證"""
    # 實際實現邏輯
    pass


@auth_email.get("/email/verify", response_model=dict)
async def verify_email(token: str, db: AsyncSession = Depends(get_async_db)):
    try:
        # 解碼 JWT token
        print("receive token")
        print(token)
        verfify_email = verify_email_token(token)

        if not verfify_email:
            raise HTTPException(status_code=400, detail="Invalid token payload")

        # 查找對應的使用者
        executor = SQLQueryExecutor(sql_loader, db)
        users = await executor.execute("GET_USER_BY_EMAIL", {"email": verfify_email})
        if not users:
            raise HTTPException(status_code=404, detail="User not found")
        user = users[0]  # ✅ 取出第一筆
        # 更新驗證狀態
        user_status = 1
        if user["user_status"] == 2:
            user_status = 3
        result = await executor.execute(
            "UPDATE_USERS_USER_STATUS",
            {"email": verfify_email, "user_status": user_status},
        )
        if not result:
            raise HTTPException(status_code=404, detail="更新使用者狀態失敗")

        return {"message": "Email verification successful"}

    except JWTError as e:
        raise HTTPException(status_code=400, detail="Invalid or expired token")


@auth_email.get("/email/status", response_model=dict)
def email_status(
    request: Request,
    email: str = Query(..., description="用戶的 Email 地址"),
):
    """
    獲取 Email 驗證狀態的 API
    """
    if not email:
        raise HTTPException(status_code=400, detail="Email is required")

    # 模擬獲取 Email 驗證狀態的邏輯
    # 實際應用中應該有查詢數據庫的邏輯

    return {"email": email, "verified": True}


@auth_email.get("/email/exists", response_model=dict)
def email_exists(
    request: Request,
    email: str = Query(..., description="用戶的 Email 地址"),
):
    """
    檢查 Email 是否已存在的 API
    """
    if not email:
        raise HTTPException(status_code=400, detail="Email is required")

    # 模擬檢查 Email 是否存在的邏輯
    # 實際應用中應該有查詢數據庫的邏輯

    exists = email == ""


@auth_email.post("/login", response_model=dict)
async def user_login(
    request: Request,
    email: str = Body(..., description="用戶的 Email 地址"),
    password: str = Body(..., description="用戶的密碼"),
    db: AsyncSession = Depends(get_async_db),
):
    """
    使用者帳號密碼登入，成功後回傳 JWT token
    """
    print(f"Login request received for email: {email}")

    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password are required")

    # 查詢使用者
    # 查詢使用者
    print(f"Checking user data for email: {email}")
    sqlString = sql_loader.get_sql("GET_USER_BY_EMAIL")
    print(f"Executing SQL: {sqlString} with email: {email}")

    # 正確的執行方式
    userData = await db.execute(text(sqlString), {"email": email})
    user = userData.mappings().fetchone()
    print(f"User data retrieved: {user}")

    if not user or not user.password_hash:
        raise HTTPException(status_code=401, detail="無效帳號")

    # if not pwd_context.verify(password, user.password_hash):
    #   raise HTTPException(status_code=401, detail="Invalid credentials")

    if user.user_status == 0:
        raise HTTPException(status_code=403, detail="使用者未認證")

    # 更新最後登入時間
    # user.last_login_at = datetime.now()
    # db.commit()

    # 產生 JWT token
    token_data = {
        "user_id": user.id,
        "email": user.email,
        "name": user.name,
        "avatar_url": user.avatar_url,
        "sub": str(user.id),
        "role_id": user.role_id,
    }

    jwt_token = create_access_token(data=token_data)

    return {
        "message": "Login successful",
        "token": jwt_token,
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "avatar_url": user.avatar_url,
            "role_id": user.role_id,
        },
    }


# 使用者 註冊帳號 需要加入驗證郵箱的功能 安全防護
@auth_email.post("/register", response_model=RegisterResponse)
async def user_register(
    payload: RegisterRequest, db: AsyncSession = Depends(get_async_db)
):
    email = payload.email
    password = payload.password

    is_email_exists = await check_email_is_exists(db, email)

    if is_email_exists:
        # 用戶存在，判斷狀態
        if is_email_exists[0]["user_status"] != 0:
            raise HTTPException(status_code=405, detail="使用者已經存在")
    else:
        # 用戶不存在，先建立新用戶（user_status=0 未驗證）
        await create_user(db, email, password)

    # 不論新用戶或舊用戶，只要尚未驗證都發送驗證信
    token = create_email_verification_token(email)
    await update_users_user_token(db, email, token)
    result = await send_verification_email(email, token)

    return RegisterResponse(
        message="Verification email sent. 請至信箱點擊驗證連結完成註冊",
        success=True,
    )


# 忘記密碼送出 forgot password
@auth_email.post("/forgotPassword", response_model=RegisterResponse)
async def forgot_password(
    payload: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_async_db),
):
    email = payload.email

    is_email_exists = await check_email_is_exists(db, email)
    if is_email_exists:
        token = create_email_verification_token(email)
        # await create_email_forget()
        print(token)
        await send_forgot_email(settings.ADMIN_EMAIL, token)
        # 假設你有一個專門處理忘記密碼重設的連結
        # reset_url = f"https://your-site.com/auth/reset-password?token={token}"
        # 寄送信件
        # await send_email(
        #     to=email,
        #     subject="🔐 密碼重設連結",
        #     html_content=f"""
        #     <p>您好，請點擊下方連結以重設您的密碼（30分鐘內有效）：</p>
        #     <a href="{reset_url}">{reset_url}</a>
        #     """,
        # )

        return RegisterResponse(success=True, message="重設密碼信已寄出")
    else:
        # 安全性考量，不透露帳號不存在
        return RegisterResponse(
            success=True, message="若該信箱存在，已寄送重設密碼信件"
        )


@auth_email.post("/resetPassword")
async def reset_password(
    token: str = Body(...),
    newPassword: str = Body(...),
    db: AsyncSession = Depends(get_async_db),
):
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"])
        email = payload.get("sub")
        print(newPassword)

        if email is None:
            raise HTTPException(status_code=400, detail="無效的 token")
        is_emali = await check_email_is_exists(db, email)
        if is_emali is None:
            raise HTTPException(status_code=400, detail="無效的 Email")
        await update_users_user_password(db, email, newPassword)
        return RegisterResponse(success=True, message="重設密碼成功請使用新密碼登錄")

    except JWTError:
        raise HTTPException(status_code=400, detail="Token 驗證失敗或已過期")

    # 查找使用者

    # result = await db.execute(select(User).where(User.email == email))
    # user = result.scalar_one_or_none()
    # if user is None:
    #    raise HTTPException(status_code=404, detail="使用者不存在")

    # 更新密碼
    # user.password_hash = pwd_context.hash(newPassword)
    # await db.commit()

    return {"message": "密碼已成功重設"}
