from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship

# 從你的資料庫設定導入 Base，而不是重新定義
from lib_db.db.database import Base

# 多對多關聯表：NavItem 與 Role
nav_item_roles = Table(
    "nav_item_roles",
    Base.metadata,
    Column("nav_item_id", Integer, ForeignKey("nav_items.id"), primary_key=True),
    Column("role_id", Integer, ForeignKey("roles.id"), primary_key=True),
)
