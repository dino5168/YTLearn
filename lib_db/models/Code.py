# lib_db/models/code_table.py

from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from lib_db.db.database import Base  # 假設你有統一的 Base


class Code(Base):
    __tablename__ = "code"

    id = Column(Integer, primary_key=True, index=True)

    category = Column(String, nullable=False)  # 代碼類別
    code = Column(String, nullable=False)  # 代碼值
    name = Column(String, nullable=False)  # 顯示名稱

    sort_order = Column(Integer, default=0)  # 排序用
    is_active = Column(Integer, default=1)  # 是否啟用（0/1）
    description = Column(Text, nullable=True)  # 備註

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
