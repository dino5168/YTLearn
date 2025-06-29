# lib_db/models/nav_item.py

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from lib_db.db.database import Base
from lib_db.models.nav_item_roles import nav_item_roles


class NavItem(Base):
    __tablename__ = "nav_items"

    id = Column(Integer, primary_key=True, index=True)
    label = Column(String, nullable=False)
    href = Column(String, nullable=True)
    order = Column(Integer, default=0)  # ✅ 加這一行！

    roles = relationship("Role", secondary=nav_item_roles, back_populates="nav_items")
    dropdowns = relationship(
        "NavDropdown", back_populates="nav_item", cascade="all, delete-orphan"
    )
