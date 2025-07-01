# user_roles.py
from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    Table,
)

# 使用你現有的 Base，而不是創建新的
from lib_db.db.database import Base

# --- 關聯表（Many-to-Many） ---
user_roles = Table(
    "user_roles",
    Base.metadata,
    Column(
        "user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    ),
    Column(
        "role_id", Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True
    ),
)
