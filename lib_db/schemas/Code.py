# lib_schemas/code_table.py

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


# 共通欄位
class CodeBase(BaseModel):
    category: str
    code: str
    name: str
    sort_order: Optional[int] = 0
    is_active: Optional[int] = 1
    description: Optional[str] = None


# 建立時用
class CodeCreate(CodeBase):
    pass


# 查詢時回傳
class CodeRead(CodeBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  #  V2


# 更新時用（所有欄位都是 Optional）
class CodeUpdate(BaseModel):
    category: Optional[str] = None
    code: Optional[str] = None
    name: Optional[str] = None
    sort_order: Optional[int] = None
    is_active: Optional[int] = None
    description: Optional[str] = None
