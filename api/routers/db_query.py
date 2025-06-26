from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

# User
from lib_db.schemas.User import UserRead  # Pydantic Schema
from lib_db.models.User import User

# Role
from lib_db.models.Role import Role
from lib_db.schemas.Role import RoleRead

from lib_db.db.get_db import get_db
from pydantic import BaseModel
from typing import List

db_query_router = APIRouter(prefix="/query", tags=["Query"])


class TokenRequest(BaseModel):
    id_token: str


@db_query_router.get("/users", response_model=List[UserRead])
def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users


@db_query_router.get("/role", response_model=List[RoleRead])
def get_users(db: Session = Depends(get_db)):
    roles = db.query(Role).all()
    return roles
