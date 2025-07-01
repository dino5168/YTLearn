from pydantic import BaseModel
from typing import Optional


class RoleBase(BaseModel):
    id: int
    name: str
    key: str
    description: Optional[str] = None


class RoleCreate(RoleBase):
    pass


class RoleUpdate(BaseModel):
    name: Optional[str] = None
    key: Optional[str] = None
    description: Optional[str] = None


class RoleRead(BaseModel):
    id: int
    name: str
    description: str | None = None  # description 是可選的

    class Config:
        orm_mode = True
