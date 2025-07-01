# lib_schemas/user_role.py
from pydantic import BaseModel
from typing import List


# 給內部參考的基本 schema
class UserRoleBase(BaseModel):
    user_id: int
    role_id: int


# 建立使用者角色關聯時使用
class UserRoleCreate(UserRoleBase):
    pass


# 查詢結果用（可擴充 id 或 created_at 等欄位）
class UserRoleRead(UserRoleBase):
    pass
