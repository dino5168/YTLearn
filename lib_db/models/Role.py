from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)  # 角色名稱（中文）
    key = Column(String, nullable=False, unique=True)  # 系統識別碼（如 "teacher"）
    description = Column(Text, nullable=True)  # 描述（可選）

    def __repr__(self):
        return f"<Role(id={self.id}, name='{self.name}', key='{self.key}')>"
