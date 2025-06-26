from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


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

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', name='{self.name}')>"
