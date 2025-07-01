from pydantic import BaseModel
from typing import Optional, List


# ---------- 共用子結構 ----------
class NavDropdownBase(BaseModel):
    label: str
    href: str


class NavDropdownCreate(NavDropdownBase):
    nav_item_id: int
    sort_order: Optional[int] = 0
    role_ids: Optional[List[int]] = []


class NavDropdownUpdate(BaseModel):
    label: Optional[str] = None
    href: Optional[str] = None
    nav_item_id: Optional[int] = None
    sort_order: Optional[int] = 0
    role_ids: Optional[List[int]] = None


class NavDropdownRead(NavDropdownBase):
    id: int
    nav_item_id: int
    roles: List[int] = []  # 或可改為 List[RoleRead] 若要回傳完整角色資料

    class Config:
        orm_mode = True


# ---------- 主選單結構 ----------
class NavItemBase(BaseModel):
    label: str
    sort_order: Optional[int] = 0
    href: Optional[str] = None


class NavItemCreate(NavItemBase):
    role_ids: Optional[List[int]] = []
    dropdowns: Optional[List[NavDropdownCreate]] = []


class NavItemUpdate(NavItemBase):
    role_ids: Optional[List[int]] = None
    dropdowns: Optional[List[NavDropdownCreate]] = None


class NavItemRead(NavItemBase):
    id: int
    roles: List[int] = []
    dropdowns: List[NavDropdownRead] = []

    class Config:
        orm_mode = True
