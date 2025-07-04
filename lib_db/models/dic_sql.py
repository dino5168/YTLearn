from sqlalchemy import (
    Column,
    Integer,
    Text,
)
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class dic_sql(Base):
    __tablename__ = "dic_sql"
    id = Column(Integer, primary_key=True, index=True)
    sqlkey = Column(Text, nullable=False)
    sqlvalue = Column(Text, nullable=False)
