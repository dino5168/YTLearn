from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Boolean,
    DateTime,
    Date,
    Numeric,
    Float,
    BigInteger,
    func,
)
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class code(Base):
    __tablename__ = "code"
    id = Column(Integer, primary_key=True, index=True)
    category = Column(Text, nullable=False)
    code = Column(Text, nullable=False)
    name = Column(Text, nullable=False)
    sort_order = Column(Integer, nullable=True, default=0)
    is_active = Column(Boolean, nullable=True, default="true")
    description = Column(Text, nullable=True)
    created_at = Column(String, nullable=True, default="CURRENT_TIMESTAMP")
    updated_at = Column(String, nullable=True, default="CURRENT_TIMESTAMP")
