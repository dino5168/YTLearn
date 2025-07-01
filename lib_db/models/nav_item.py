# lib_db/models/nav_item.py

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from lib_db.db.database import Base
from lib_db.models.nav_item_roles import nav_item_roles


class NavItem(Base):
    __tablename__ = "nav_items"

    id = Column(Integer, primary_key=True, index=True)
    label = Column(String, nullable=False)
    href = Column(String, nullable=True)
    sort_order = Column(Integer, default=0)  # ✅ 加這一行！
    dropdowns = relationship(
        "NavDropdown", back_populates="nav_item", cascade="all, delete-orphan"
    )
    # role_id = Column(Integer, ForeignKey("roles.id"))
    roles = relationship("Role", secondary=nav_item_roles, back_populates="nav_items")
    dropdowns = relationship(
        "NavDropdown",
        back_populates="nav_item",
        cascade="all, delete-orphan",
        order_by="NavDropdown.sort_order",  # ✅ 加這行來排序 dropdowns
    )
