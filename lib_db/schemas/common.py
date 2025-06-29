# schemas/common.py
from pydantic import BaseModel


class ComboBoxOption(BaseModel):
    label: str
    value: int | str
