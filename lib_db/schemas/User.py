from pydantic import BaseModel, EmailStr, AnyUrl
from typing import Optional, List
from datetime import datetime
from lib_db.schemas.Role import RoleRead


# 共通欄位
class UserBase(BaseModel):
    email: EmailStr
    name: Optional[str] = None
    avatar_url: Optional[AnyUrl] = None
    google_id: Optional[str] = None


# 建立時使用（輸入用）
class UserCreate(UserBase):
    pass  # 若日後要加入密碼或角色，可以擴充


# 輸出用
class UserRead(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime
    is_active: bool
    roles: List[RoleRead] = []

    class Config:
        orm_mode = True  # 讓 Pydantic 能接收 SQLAlchemy 物件
