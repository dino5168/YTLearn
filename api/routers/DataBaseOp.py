from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List, Optional

from lib_db.db.database import get_db
from lib_db.models.Code import Code
from lib_db.schemas.Code import CodeCreate, CodeUpdate, CodeRead
from lib_services.code_service import CodeService  # 假設你的 service 放這裡

databaseop_router = APIRouter(prefix="/DatabaseOp", tags=["DatabaseOp"])


@databaseop_router.post(
    "/codepost", response_model=CodeRead, status_code=status.HTTP_201_CREATED
)
def create_code(code_data: CodeCreate, db: Session = Depends(get_db)):

    service = CodeService(db)
    return service.create(code_data)


@databaseop_router.get("/code", response_model=List[CodeRead])
def read_codes(category: Optional[str] = None, db: Session = Depends(get_db)):
    service = CodeService(db)
    return service.get_all(category)


@databaseop_router.get("/code/{code_id}", response_model=CodeRead)
def read_code(code_id: int, db: Session = Depends(get_db)):
    service = CodeService(db)
    return service.get_by_id(code_id)


@databaseop_router.put("/codeput/{code_id}", response_model=CodeRead)
def update_code(code_id: int, update_data: CodeUpdate, db: Session = Depends(get_db)):
    service = CodeService(db)
    return service.update(code_id, update_data)


@databaseop_router.delete(
    "/codedelete/{code_id}", status_code=status.HTTP_204_NO_CONTENT
)
def delete_code(code_id: int, db: Session = Depends(get_db)):
    service = CodeService(db)
    service.delete(code_id)
    return None
