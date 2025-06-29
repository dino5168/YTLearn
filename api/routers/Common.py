# routers/role.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from lib_db.db.database import get_db
from lib_db.models.role import Role
from lib_db.schemas.common import ComboBoxOption


common_router = APIRouter(prefix="/common", tags=["common"])


@common_router.get("/roles", response_model=list[ComboBoxOption])
def get_roles_for_combo(db: Session = Depends(get_db)):
    roles = db.query(Role).all()
    return [{"label": role.name, "value": role.id} for role in roles]
