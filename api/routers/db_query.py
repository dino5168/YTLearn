from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

# User
from lib_db.schemas.User import UserRead  # Pydantic Schema
from lib_db.models.User import User

# Role
from lib_db.models.role import Role
from lib_db.schemas.Role import RoleRead

# Import NavItemRead schema
from lib_db.models.nav_item import NavItem
from lib_db.schemas.Nav_Items import NavItemRead

from lib_db.db.database import get_db
from lib_util.Auth import get_current_user  # Import the dependency
from pydantic import BaseModel
from typing import List

db_query_router = APIRouter(prefix="/query", tags=["Query"])


class TokenRequest(BaseModel):
    id_token: str


@db_query_router.get("/usersV1", response_model=List[UserRead])
def get_users(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    users = db.query(User).all()
    return users


@db_query_router.get("/users", response_model=List[UserRead])
def get_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),  # 這行會自動驗證 JWT
):
    users = db.query(User).all()
    return users


@db_query_router.get("/role", response_model=List[RoleRead])
def get_roles(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        roles = db.query(Role).all()
        return roles
    except Exception as e:
        print("Error:", e)
        raise e


@db_query_router.get("/nav_items", response_model=List[NavItemRead])
def get_nav_items(
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_user),
):
    try:
        NavItems = db.query(NavItem).all()
        return NavItems
    except Exception as e:
        print("Error:", e)
        raise e
