from pydantic import BaseModel, Field
from typing import Optional


# 建立用
class CreateCode(BaseModel):
    type: str = Field(..., example="gender")
    code: str = Field(..., example="M")
    label: str = Field(..., example="男")
    description: Optional[str] = Field(None, example="男性")
    is_active: Optional[bool] = Field(True, example=True)
    order: Optional[int] = Field(None, example=1)


# 更新用：所有欄位皆為 Optional，id 由路由參數給
class UpdateCode(BaseModel):
    type: Optional[str] = Field(None, example="gender")
    code: Optional[str] = Field(None, example="F")
    label: Optional[str] = Field(None, example="女")
    description: Optional[str] = Field(None, example="女性")
    is_active: Optional[bool] = Field(None, example=False)
    order: Optional[int] = Field(None, example=2)


# 讀取（Read）用：包含 id
class Code(BaseModel):
    id: int
    type: str
    code: str
    label: str
    description: Optional[str]
    is_active: bool
    order: Optional[int]

    class Config:
        orm_mode = True


# 刪除用：僅需傳 id
class DeleteCode(BaseModel):
    id: int
