from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from lib_db.models.Code import Code
from lib_db.schemas.Code import CodeCreate, CodeUpdate


class CodeService:
    def __init__(self, db: Session):
        self.db = db

    def create(self, code_data: CodeCreate) -> Code:
        db_code = Code(**code_data.dict())
        self.db.add(db_code)
        self.db.commit()
        self.db.refresh(db_code)
        return db_code

    def get_all(self, category: str = None) -> list[Code]:
        query = self.db.query(Code)
        if category:
            query = query.filter(Code.category == category)
        return query.order_by(Code.sort_order).all()

    def get_by_id(self, code_id: int) -> Code:
        db_code = self.db.query(Code).filter(Code.id == code_id).first()
        if not db_code:
            raise HTTPException(status_code=404, detail="代碼不存在")
        return db_code

    def update(self, code_id: int, update_data: CodeUpdate) -> Code:
        db_code = self.get_by_id(code_id)
        for field, value in update_data.dict(exclude_unset=True).items():
            setattr(db_code, field, value)
        self.db.commit()
        self.db.refresh(db_code)
        return db_code

    def delete(self, code_id: int) -> None:
        db_code = self.get_by_id(code_id)
        self.db.delete(db_code)
        self.db.commit()
