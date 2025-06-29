from sqlalchemy import Column, Integer, String, Boolean
from lib_db.db.database import Base


class CodeTable(Base):
    __tablename__ = "code_table"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(50), nullable=False)  # 代碼類別，如 gender, status
    code = Column(String(50), nullable=False)  # 代碼值，如 M, F, 1, 0
    label = Column(String(100), nullable=False)  # 顯示名稱
    description = Column(String(255), nullable=True)  # 補充說明
    is_active = Column(Boolean, default=True)  # 是否啟用
    order = Column(Integer, nullable=True)  # 顯示排序（選填）

    def __repr__(self):
        return (
            f"<CodeTable(type='{self.type}', code='{self.code}', label='{self.label}')>"
        )
