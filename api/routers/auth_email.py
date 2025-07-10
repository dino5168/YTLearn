from datetime import datetime

# from pydoc import text

from sqlalchemy import text

from fastapi import APIRouter, Body, HTTPException, Depends, Request, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from api.routers.auth_google import create_access_token
from lib_db.db.database import get_async_db
from lib_db.models.User import User
from lib_sql.sql_loader_singleton import get_sql_loader
from lib_sql.SQLQueryExecutor import SQLQueryExecutor

sql_loader = get_sql_loader()


auth_email = APIRouter(prefix="/auth", tags=["auth"])


# 建議使用 Pydantic 模型來定義請求結構
class RegisterRequest(BaseModel):
    email: str = Field(..., description="用戶的 Email 地址")
    password: str = Field(..., description="用戶的密碼", min_length=6, max_length=10)


class RegisterResponse(BaseModel):
    message: str
    success: bool = True


# 輔助函數（需要根據實際情況實現）
async def check_email_is_exists(db: AsyncSession, email: str) -> bool:
    """檢查郵箱是否存在於資料庫中"""
    # 實際實現邏輯
    if not email:
        raise HTTPException(status_code=400, detail="Email is required")

    # 使用 SQL 查詢檢查 Email 是否存在
    # 這裡假設有一個 SQL 查詢語句 "CHECK_USER_EMAIL" 用於檢查 Email
    # 執行 SQL 查詢
    # 注意：這裡的 "CHECK_USER_EMAIL" 是一個 SQL 查詢語句的名稱，
    # 需要在 SQL 文件中定義這個查詢語句。
    print(f"Checking if email exists: {email}")
    if not db:
        raise HTTPException(status_code=500, detail="Database connection error")
    # 使用 SQLQueryExecutor 執行 SQL 查詢
    # 假設 SQLQueryExecutor 已經實現了執行 SQL 查詢
    executor = SQLQueryExecutor(sql_loader, db)
    result = await executor.execute("CHECK_USER_EMAIL", {"email": email})
    print(f"Email exists check result: {result}")

    # 模擬檢查 Email 是否存在的邏輯
    # 實際應用中應該有查詢數據庫的邏輯
    if result is not None and len(result) > 0:
        return True
    return False


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
async def create_user(db: AsyncSession, email: str, password: str) -> None:
    """創建新用戶"""
    print("create_user")
    print(f"Creating user with email: {email} and password hash: {password}")
    executor = SQLQueryExecutor(sql_loader, db)
    result = await executor.execute(
        "INSERT_USER_BY_REGISTER", {"email": email, "password_hash": password}
    )


async def check_user_email_verification_status(db: AsyncSession, email: str) -> bool:
    """檢查用戶郵箱是否已驗證"""
    # 實際實現邏輯
    pass


async def send_verification_email(email: str) -> bool:
    """發送驗證郵件"""
    # 實際實現邏輯
    pass


@auth_email.get("/email/verify", response_model=dict)
def verify_email(
    request: Request,
    token: str = Query(..., description="驗證 token"),
):
    """
    驗證 Email 的 API
    """
    # 這裡應該有驗證 token 的邏輯
    # 假設驗證成功，返回成功訊息
    if not token:
        raise HTTPException(status_code=400, detail="Token is required")

    # 模擬驗證邏輯
    if token == "valid_token":
        return {"message": "Email verified successfully"}

    raise HTTPException(status_code=400, detail="Invalid token")


# 使用者 註冊帳號 需要加入驗證郵箱的功能 安全防護
@auth_email.post("/register", response_model=RegisterResponse)
async def user_register(
    payload: RegisterRequest, db: AsyncSession = Depends(get_async_db)
):
    """
    使用者註冊帳號的 API
    這個 API 檢查郵箱是否存在，並發送驗證
    """
    try:
        print(f"Check email exists payload: {payload.email}")

        # 修正：統一使用 payload.email 而不是 payload dict
        email = payload.email

        # 檢查郵箱是否存在（假設這個函數需要調整參數）
        # 原代碼中 check_email_is_exists 的調用方式不一致
        is_email_exists = await check_email_is_exists(db, email)

        if not is_email_exists:
            # 如果郵箱不存在，則創建新用戶
            # 發送驗證郵件
            await create_user(db, email, payload.password)
            print(f"Email {email} does not exist")
        else:
            # 如果郵箱已存在，則直接綁定帳號
            print(f"Email {email} already exists, sending verification email")
            # await bind_account_to_email(db, email, payload.password)

        # raise HTTPException(status_code=404, detail="Email not found")
        return RegisterResponse(
            message="Email exists, verification email sent", success=True
        )

        # 檢查用戶是否已經驗證過郵箱
        # is_user_verified = await check_user_email_verification_status(db, email)

        # if is_user_verified:
        #   return EmailVerificationResponse(
        #      message="Email is already verified", success=True
        #    )

        # 重新發送驗證郵件
        # 實際應用中應該：
        # 1. 生成新的驗證 token
        # 2. 更新資料庫中的 token 記錄
        # 3. 發送郵件

    except HTTPException:
        raise
    except Exception as e:
        print(f"Resend verification email error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


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


@auth_email.post("/login_", response_model=dict)
def user_login(
    request: Request,
    email: str = Body(..., description="用戶的 Email 地址"),
    password: str = Body(..., description="用戶的密碼"),
):
    """
    使用者登入帳號的 API
    """
    print(f"Login request received for email: {email}")
    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password are required")

    # 模擬登入邏輯
    # 實際應用中應該有查詢數據庫的邏輯

    return {"message": "Login successful", "email": email}


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
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # if not pwd_context.verify(password, user.password_hash):
    #   raise HTTPException(status_code=401, detail="Invalid credentials")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="User account is inactive")

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
