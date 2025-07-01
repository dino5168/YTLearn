from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from lib_db.schemas.user_role import UserRoleCreate, UserRoleRead
from lib_db.db.database import get_db  # 你定義的 get_db function
from lib_db.models.user_roles import user_roles  # 關聯表 Table
from lib_db.models.User import User
from lib_db.models.role import Role
from fastapi import status

db_create_router = APIRouter(prefix="/Create", tags=["Create"])


@db_create_router.post(
    "/UserRole", response_model=List[UserRoleRead], status_code=status.HTTP_201_CREATED
)
def create_user_roles(
    user_roles_data: List[UserRoleCreate], db: Session = Depends(get_db)
):
    created = []
    for user_role in user_roles_data:
        # 檢查 user 是否存在
        user = db.query(User).filter(User.id == user_role.user_id).first()
        if not user:
            raise HTTPException(
                status_code=404, detail=f"User {user_role.user_id} not found"
            )

        # 檢查 role 是否存在
        role = db.query(Role).filter(Role.id == user_role.role_id).first()
        if not role:
            raise HTTPException(
                status_code=404, detail=f"Role {user_role.role_id} not found"
            )

        # 先刪除舊的（若存在）
        db.execute(
            user_roles.delete().where(
                (user_roles.c.user_id == user_role.user_id)
                & (user_roles.c.role_id == user_role.role_id)
            )
        )
        # 插入新關聯
        db.execute(
            user_roles.insert().values(
                user_id=user_role.user_id, role_id=user_role.role_id
            )
        )
        created.append(user_role)

    db.commit()
    return created
