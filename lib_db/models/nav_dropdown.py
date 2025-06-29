# lib_db/models/nav_dropdown.py

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from lib_db.db.database import Base
from lib_db.models.nav_dropdown_roles import nav_dropdown_roles


class NavDropdown(Base):
    __tablename__ = "nav_dropdowns"

    id = Column(Integer, primary_key=True, index=True)
    label = Column(String, nullable=False)
    href = Column(String, nullable=True)
    nav_item_id = Column(Integer, ForeignKey("nav_items.id"), nullable=False)
    order = Column(Integer, default=0)  # 排序欄位

    nav_item = relationship("NavItem", back_populates="dropdowns")
    roles = relationship(
        "Role", secondary=nav_dropdown_roles, back_populates="nav_dropdowns"
    )
