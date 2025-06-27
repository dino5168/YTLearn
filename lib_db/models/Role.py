# lib_db/models/Role.py
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

# 從你的資料庫設定導入 Base
from lib_db.db.database import Base

# 導入關聯表（延遲導入以避免循環依賴）


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=True)

    # 使用延遲載入的關聯表引用
    nav_items = relationship(
        "NavItem", secondary="nav_item_roles", back_populates="roles"  # 使用表名字串
    )

    nav_dropdowns = relationship(
        "NavDropdown",
        secondary="nav_dropdown_roles",  # 使用表名字串
        back_populates="roles",
    )
