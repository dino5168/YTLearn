from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, func

from sqlalchemy.orm import relationship, declarative_base
from lib_db.models.user_roles import user_roles

Base = declarative_base()

#2025-07-06 加入 role_id
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=True)
    avatar_url = Column(Text, nullable=True)
    google_id = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    is_active = Column(Boolean, default=True)
    role_id = Column(Integer,nullable=True) 

    # 多對多關聯
    # roles = relationship(Role, secondary=user_roles, back_populates="users")
    # 多對多關聯到 Role
    #
    # nav_dropdowns = relationship(
    #   "NavDropdown",
    #   secondary="nav_dropdown_roles",
    #   back_populates="roles",
    # )

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', name='{self.name}')>"
