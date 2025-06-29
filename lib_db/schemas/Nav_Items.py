from pydantic import BaseModel
from typing import Optional, List


# ---------- 共用子結構 ----------
class NavDropdownBase(BaseModel):
    label: str
    href: str
    order: Optional[int] = 0  # 顯示順序，預設為 0


class NavDropdownCreate(NavDropdownBase):
    nav_item_id: int
    role_ids: Optional[List[int]] = []


# ---------- 主選單共用欄位 ----------
class NavItemBase(BaseModel):
    label: str  # 主選單名稱
    href: Optional[str] = None  # 主選單連結（可為 None）
    order: Optional[int] = 0  # 顯示順序，預設為 0


# ---------- 建立主選單 ----------
class NavItemCreate(NavItemBase):
    pass


# ---------- 更新主選單 ----------
class NavItemUpdate(BaseModel):
    label: Optional[str] = None
    href: Optional[str] = None
    order: Optional[int] = None
    role_ids: Optional[List[int]] = None
    dropdowns: Optional[List[NavDropdownCreate]] = None


# ---------- 讀取主選單 ----------
class NavItemRead(NavItemBase):
    id: int

    class Config:
        orm_mode = True
