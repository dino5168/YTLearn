# lib_db/models/nav_items_roles.py
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

# 多對多關聯表：NavDropdown 與 Role
nav_dropdown_roles = Table(
    "nav_dropdown_roles",
    Base.metadata,
    Column(
        "nav_dropdown_id", Integer, ForeignKey("nav_dropdowns.id"), primary_key=True
    ),
    Column("role_id", Integer, ForeignKey("roles.id"), primary_key=True),
)


class NavItem(Base):
    __tablename__ = "nav_items"

    id = Column(Integer, primary_key=True, index=True)
    label = Column(String, nullable=False)
    href = Column(String, nullable=True)

    # 使用字串引用避免循環導入問題
    roles = relationship("Role", secondary=nav_item_roles, back_populates="nav_items")

    dropdowns = relationship(
        "NavDropdown", back_populates="nav_item", cascade="all, delete-orphan"
    )


class NavDropdown(Base):
    __tablename__ = "nav_dropdowns"

    id = Column(Integer, primary_key=True, index=True)
    label = Column(String, nullable=False)
    href = Column(String, nullable=True)
    nav_item_id = Column(Integer, ForeignKey("nav_items.id"), nullable=False)

    # 使用字串引用
    nav_item = relationship("NavItem", back_populates="dropdowns")
    roles = relationship(
        "Role", secondary=nav_dropdown_roles, back_populates="nav_dropdowns"
    )
