# lib_db/models/Role.py
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

# 從你的資料庫設定導入 Base
from lib_db.db.database import Base

# 導入關聯表
# from lib_db.models.user_roles import user_roles


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=True)
    # 確保有正確的關係定義

    # 使用延遲載入的關聯表引用
    nav_items = relationship(
        "NavItem", secondary="nav_item_roles", back_populates="roles"
    )

    nav_dropdowns = relationship(
        "NavDropdown",
        secondary="nav_dropdown_roles",
        back_populates="roles",
    )

    # 新增的 users 關聯 - 使用導入的 user_roles 表
    # users = relationship("User", secondary="user_roles", back_populates="roles")
    # users = relationship("Users", secondary=user_roles, back_populates="roles")
