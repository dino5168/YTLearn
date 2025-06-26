from pydantic import BaseModel
from typing import Optional


class RoleBase(BaseModel):
    name: str
    key: str
    description: Optional[str] = None


class RoleCreate(RoleBase):
    pass


class RoleUpdate(BaseModel):
    name: Optional[str] = None
    key: Optional[str] = None
    description: Optional[str] = None


class RoleRead(RoleBase):
    id: int

    class Config:
        orm_mode = True
