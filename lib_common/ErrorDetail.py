from pydantic import BaseModel
from typing import Optional

# 錯誤訊息模型


class ErrorDetail(BaseModel):
    code: str  # 錯誤代碼，例如 "unauthorized"、"not_found"
    message: str  # 錯誤訊息
    hint: Optional[str] = None  # 提示訊息，可選
