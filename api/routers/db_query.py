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
from lib_db.db.database import get_async_db
from lib_util.Auth import get_current_user  # Import the dependency
from pydantic import BaseModel
from typing import List
from lib_db.respository.code_repository import CodeRepository
from lib_sql.sql_loader_singleton import get_sql_loader
from lib_sql.SQLQueryExecutor import SQLQueryExecutor

sql_loader = get_sql_loader()

db_query_router = APIRouter(prefix="/query", tags=["Query"])
# sql_loader = get_sql_loader()  # Removed because get_sql_loader is not defined


class TokenRequest(BaseModel):
    id_token: str


@db_query_router.get("/usersV1", response_model=List[UserRead])
def get_users(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    users = db.query(User).all()
    return users


# 取得使用者列表 舊版方式
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


@db_query_router.get("/all/{sql_key}")
async def get_code_data_all(
    sql_key: str,
    db: Session = Depends(get_async_db),
):
    # sql = sql_loader.get_sql("SELECT_CODE_ALL")
    try:
        executor = SQLQueryExecutor(sql_loader, db)
        result = await executor.execute(sql_key)
        return result
    except Exception as e:
        raise e
