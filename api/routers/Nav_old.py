from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import asc

from lib_db.db.database import SessionLocal
from lib_db.models.nav_item import NavItem
from lib_db.models.nav_dropdown import NavDropdown
from lib_db.models.role import Role
from lib_db.schemas.nav import NavItemCreate, NavItemRead, NavItemUpdate
from lib_db.schemas.nav import NavDropdownCreate, NavDropdownRead, NavDropdownUpdate

# from lib_db.schemas.nav import NavItemRoleLinkCreate

from typing import List
from lib_util.Auth import get_current_user  # Import the dependency
from lib_db.models.User import User
from lib_db.db.database import get_db
from lib_db.db.database import get_async_db
import logging

nav_router = APIRouter(prefix="/nav", tags=["Navigation"])
logger = logging.getLogger(__name__)


# 取得所有主選單（含 dropdown 與角色 id）
@nav_router.get("/items", response_model=List[NavItemRead])
def get_nav_items(db: Session = Depends(get_db)):
    try:
        return db.query(NavItem).all()
    except SQLAlchemyError as e:
        logger.error(f"Database error in get_nav_items: {e}")
        raise HTTPException(status_code=500, detail="Database error")


# 建立主選單 + dropdown + 角色
@nav_router.post("/items", response_model=NavItemRead)
def create_nav_item(data: NavItemCreate, db: Session = Depends(get_db)):
    try:
        nav_item = NavItem(label=data.label, href=data.href)

        # 指派角色（多對多）- 加入存在性檢查
        if data.role_ids:
            roles = db.query(Role).filter(Role.id.in_(data.role_ids)).all()
            if len(roles) != len(data.role_ids):
                raise HTTPException(status_code=400, detail="Some role IDs not found")
            nav_item.roles = roles

        # 建立子選單
        for d in data.dropdowns or []:
            dropdown = NavDropdown(label=d.label, href=d.href)
            # 檢查 dropdown 的角色是否存在
            if d.role_ids:
                dropdown_roles = db.query(Role).filter(Role.id.in_(d.role_ids)).all()
                if len(dropdown_roles) != len(d.role_ids):
                    raise HTTPException(
                        status_code=400, detail="Some dropdown role IDs not found"
                    )
                dropdown.roles = dropdown_roles
            nav_item.dropdowns.append(dropdown)

        db.add(nav_item)
        db.commit()
        db.refresh(nav_item)
        return nav_item

    except HTTPException:
        raise
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error in create_nav_item: {e}")
        raise HTTPException(status_code=500, detail="Database error")


# 取得單一主選單
@nav_router.get("/items/{item_id}", response_model=NavItemRead)
def get_nav_item(item_id: int, db: Session = Depends(get_db)):
    try:
        item = db.query(NavItem).filter(NavItem.id == item_id).first()
        if not item:
            raise HTTPException(status_code=404, detail="Nav item not found")
        return item
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error in get_nav_item: {e}")
        raise HTTPException(status_code=500, detail="Database error")


# 更新主選單 + dropdown + 角色
@nav_router.put("/items/{item_id}", response_model=NavItemRead)
def update_nav_item(item_id: int, data: NavItemUpdate, db: Session = Depends(get_db)):
    try:
        item = db.query(NavItem).filter(NavItem.id == item_id).first()
        if not item:
            raise HTTPException(status_code=404, detail="Nav item not found")

        if data.label is not None:
            item.label = data.label
        if data.href is not None:
            item.href = data.href
        if data.role_ids is not None:
            roles = db.query(Role).filter(Role.id.in_(data.role_ids)).all()
            if len(roles) != len(data.role_ids):
                raise HTTPException(status_code=400, detail="Some role IDs not found")
            item.roles = roles

        # 更新 dropdown（明確刪除舊的記錄）
        if data.dropdowns is not None:
            # 明確刪除舊的 dropdowns
            for dropdown in item.dropdowns[:]:  # 使用切片複製避免修改迭代中的列表
                db.delete(dropdown)
            db.flush()  # 確保刪除操作完成

            # 建立新的 dropdowns
            item.dropdowns = []
            for d in data.dropdowns:
                dropdown = NavDropdown(label=d.label, href=d.href)
                if d.role_ids:
                    dropdown_roles = (
                        db.query(Role).filter(Role.id.in_(d.role_ids)).all()
                    )
                    if len(dropdown_roles) != len(d.role_ids):
                        raise HTTPException(
                            status_code=400, detail="Some dropdown role IDs not found"
                        )
                    dropdown.roles = dropdown_roles
                item.dropdowns.append(dropdown)

        db.commit()
        db.refresh(item)
        return item

    except HTTPException:
        raise
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error in update_nav_item: {e}")
        raise HTTPException(status_code=500, detail="Database error")


# 刪除主選單（連同 dropdown）
@nav_router.delete("/items/{item_id}")
def delete_nav_item(item_id: int, db: Session = Depends(get_db)):
    try:
        item = db.query(NavItem).filter(NavItem.id == item_id).first()
        if not item:
            raise HTTPException(status_code=404, detail="Nav item not found")
        db.delete(item)
        db.commit()
        return {"detail": "Nav item deleted"}
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error in delete_nav_item: {e}")
        raise HTTPException(status_code=500, detail="Database error")


from sqlalchemy import text
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from lib_db.db.database import get_db  # 你的資料庫依賴
import logging

# nav_router = APIRouter()
nav_router = APIRouter(prefix="/nav", tags=["Navigation"])
logger = logging.getLogger(__name__)


@nav_router.get("/links")
def get_nav_links(db: Session = Depends(get_db)):  # 改用 get_db 而非 get_async_db
    logger.info("使用純 SQL 查詢 nav_items + nav_dropdowns")
    try:
        raw_sql = """
        SELECT 
          ni.id,
          ni.label,
          ni.href,
          ni.sort_order,
          COALESCE(
            json_agg(
              json_build_object(
                'id', nd.id,
                'label', nd.label,
                'href', nd.href,
                'type', '1',
                'nav_item_id', nd.nav_item_id,
                'sort_order', nd.sort_order
              ) ORDER BY nd.sort_order
            ) FILTER (WHERE nd.id IS NOT NULL),
            '[]'
          ) AS dropdown
        FROM nav_items ni
        LEFT JOIN nav_dropdowns nd
          ON nd.nav_item_id = ni.id
        GROUP BY ni.id, ni.label, ni.href, ni.sort_order
        ORDER BY ni.sort_order;
        """

        result = db.execute(text(raw_sql))
        nav_items = []
        for row in result:
            item = {
                "id": row.id,
                "label": row.label,
                "type": "0",
                "nav_item_id": "0",
                "sort_order": row.sort_order,
            }

            # 處理 dropdown 資料
            dropdown_data = row.dropdown
            if isinstance(dropdown_data, str):
                import json

                dropdown_data = json.loads(dropdown_data)

            # 如果有 dropdown，加入 dropdown；否則加入 href
            if dropdown_data and len(dropdown_data) > 0:
                item["dropdown"] = dropdown_data
            else:
                item["href"] = row.href

            nav_items.append(item)

        return nav_items

    except SQLAlchemyError as e:
        logger.error(f"SQLAlchemy error in get_nav_links: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error")
    except Exception as e:
        logger.error(f"Unexpected error in get_nav_links: {str(e)}")
        raise HTTPException(status_code=500, detail="Unexpected error")


# 從資料庫讀取 nav_items 與 nav_dropdowns，回傳簡單結構
@nav_router.get("/links_old")
def get_nav_links(db: Session = Depends(get_db)):
    logger.info("從資料庫讀取 nav_items 與 nav_dropdowns，回傳簡單結構")
    try:
        # 測試資料庫連接
        logger.info("Attempting to query NavItem table")
        # nav_items = db.query(NavItem).all()
        nav_items = db.query(NavItem).order_by(asc(NavItem.sort_order)).all()
        logger.info(f"Successfully retrieved {len(nav_items)} nav items")

        result = []
        for item in nav_items:
            try:
                if item.dropdowns:
                    dropdown = [
                        {
                            "label": d.label,
                            "href": d.href,
                            "type": "1",
                            "id": d.id,
                            "nav_item_id": d.nav_item_id,
                            "sort_order": d.sort_order,
                        }
                        for d in item.dropdowns
                    ]
                    result.append(
                        {
                            "label": item.label,
                            "id": item.id,
                            "type": "0",
                            "nav_item_id": "0",
                            "sort_order": item.sort_order,
                            "dropdown": dropdown,
                        }
                    )
                else:
                    result.append(
                        {
                            "label": item.label,
                            "href": item.href,
                            "type": "0",
                            "id": item.id,
                            "nav_item_id": "0",
                            "sort_order": item.sort_order,
                        }
                    )
            except Exception as item_error:
                logger.error(f"Error processing nav item {item.id}: {item_error}")
                continue

        logger.info(f"Returning {len(result)} processed nav items")
        return result
    except SQLAlchemyError as e:
        logger.error(f"SQLAlchemy error in get_nav_links: {str(e)}")
        logger.error(f"Error type: {type(e)}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error in get_nav_links: {str(e)}")
        logger.error(f"Error type: {type(e)}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


# 診斷端點 - 用於檢查資料庫連接和模型
@nav_router.get("/debug/db-status")
def debug_db_status(db: Session = Depends(get_db)):
    """診斷資料庫連接和模型狀態"""
    try:
        # 1. 測試基本資料庫連接
        db.execute("SELECT 1")
        logger.info("Database connection: OK")

        # 2. 檢查表是否存在
        try:
            nav_count = db.query(NavItem).count()
            logger.info(f"NavItem table accessible, count: {nav_count}")
        except Exception as e:
            logger.error(f"NavItem table error: {e}")
            return {"error": f"NavItem table error: {str(e)}"}

        # 3. 檢查關聯表
        try:
            dropdown_count = db.query(NavDropdown).count()
            logger.info(f"NavDropdown table accessible, count: {dropdown_count}")
        except Exception as e:
            logger.error(f"NavDropdown table error: {e}")
            return {"error": f"NavDropdown table error: {str(e)}"}

        # 4. 檢查 Role 表
        try:
            role_count = db.query(Role).count()
            logger.info(f"Role table accessible, count: {role_count}")
        except Exception as e:
            logger.error(f"Role table error: {e}")
            return {"error": f"Role table error: {str(e)}"}

        # 5. 測試簡單查詢
        try:
            first_nav = db.query(NavItem).first()
            if first_nav:
                logger.info(f"First nav item: {first_nav.label}")
            else:
                logger.info("No nav items found")
        except Exception as e:
            logger.error(f"Query error: {e}")
            return {"error": f"Query error: {str(e)}"}

        return {
            "database_connection": "OK",
            "nav_items_count": nav_count,
            "dropdowns_count": dropdown_count,
            "roles_count": role_count,
            "first_nav_item": first_nav.label if first_nav else None,
        }

    except Exception as e:
        logger.error(f"Debug endpoint error: {e}")
        return {"error": f"Debug error: {str(e)}"}


# 簡化版本的 links 端點（不使用關聯）
@nav_router.get("/links-simple")
def get_nav_links_simple(db: Session = Depends(get_db)):
    """簡化版本，不使用關聯查詢"""
    print("簡化版本，不使用關聯查詢")
    try:
        # 只查詢基本欄位，不載入關聯
        nav_items = db.query(NavItem.id, NavItem.label, NavItem.href).all()
        logger.info(f"Retrieved {len(nav_items)} nav items (simple)")

        result = []
        for item in nav_items:
            result.append({"id": item.id, "label": item.label, "href": item.href})

        return result

    except Exception as e:
        logger.error(f"Error in get_nav_links_simple: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


# 靜態版本的導航連結（保留作為備用）
@nav_router.get("/linksV1")
def get_nav_links_static():
    return [
        {"label": "首頁", "href": "/"},
        {
            "label": "如何學習",
            "dropdown": [
                {"label": "初學者的提示", "href": "/html/Learn50tips"},
                {"label": "有效學習", "href": "/html/learningtw"},
                {"label": "高效學習-6個月", "href": "/html/LearnSixMonth.html"},
                {"label": "不要害羞恐懼", "href": "/html/Learninglanguage"},
            ],
        },
        {
            "label": "學習",
            "dropdown": [
                {"label": "字典查詢", "href": "/dict/hello"},
                {"label": "文法訓練", "href": "/tools/GrammarCheck"},
                {"label": "英文打字練習", "href": "/tools/typegame"},
                {"label": "錄音練習", "href": "/voices/VoiceRecorder"},
            ],
        },
        {
            "label": "老師",
            "dropdown": [
                {"label": "影片匯入", "href": "/admin/download"},
                {"label": "字幕修正", "href": "/admin/manageSrt"},
                {"label": "影片列表", "href": "/admin/videoList"},
                {"label": "音訊轉文字", "href": "/tools/mp32text"},
                {"label": "文字轉音訊", "href": "/tools/text2mp3"},
            ],
        },
        {
            "label": "家長",
            "dropdown": [
                {"label": "影片匯入", "href": "/admin/download"},
                {"label": "字幕修正", "href": "/admin/manageSrt"},
                {"label": "影片列表", "href": "/admin/videoList"},
                {"label": "音訊轉文字", "href": "/tools/mp32text"},
                {"label": "文字轉音訊", "href": "/tools/text2mp3"},
            ],
        },
        {
            "label": "系統管理",
            "dropdown": [
                {"label": "帳號管理", "href": "/user/UserList"},
                {"label": "角色管理", "href": "/user/RoleList"},
            ],
        },
        {"label": "關於我們", "href": "/aboutus"},
    ]


# 更新主選單
@nav_router.put("/updateNav0/{item_id}", response_model=NavItemRead)
def update_nav_item(
    item_id: int,
    nav_item_update: NavItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    db_item = db.query(NavItem).filter(NavItem.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="NavItem not found")

    db_item.label = nav_item_update.label
    db_item.href = nav_item_update.href
    db_item.sort_order = nav_item_update.sort_order

    db.commit()

    db.refresh(db_item)

    return db_item


# 更新副選單
@nav_router.put("/updateNav1/{item_id}", response_model=NavDropdownRead)
def update_nav_dropdown(
    item_id: int,
    nav_item_update: NavDropdownUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # print("updateNav1")

    db_item = (
        db.query(NavDropdown)
        .filter(
            NavDropdown.id == item_id,
            NavDropdown.nav_item_id == nav_item_update.nav_item_id,
        )
        .first()
    )

    if not db_item:
        raise HTTPException(status_code=404, detail="NavDropdown not found")
    logger.info("update sub menu")
    logger.info(nav_item_update.sort_order)
    db_item.label = nav_item_update.label
    db_item.href = nav_item_update.href
    db_item.sort_order = nav_item_update.sort_order

    db.commit()
    db.refresh(db_item)

    return db_item


# 新增主選單
@nav_router.post("/createNav0", response_model=NavItemRead)
def create_nav_item(
    nav_item_create: NavItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    print("createNav0")
    db_item = NavItem(
        label=nav_item_create.label,
        href=nav_item_create.href,
        sort_order=nav_item_create.sort_order,
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


# 新增副選單
@nav_router.post("/createNav1", response_model=NavDropdownRead)
def create_nav_item(
    nav_item_create: NavDropdownCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    print("createNav1")
    print(nav_item_create.nav_item_id)
    db_item = NavDropdown(
        label=nav_item_create.label,
        href=nav_item_create.href,
        nav_item_id=nav_item_create.nav_item_id,
        sort_order=nav_item_create.sort_order,
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


@nav_router.delete("/deleteNav0/{item_id}", response_model=NavItemRead)
def delete_nav_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    print("deleteNav0")
    db_item = db.query(NavItem).filter(NavItem.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="NavItem not found")

    db.delete(db_item)
    db.commit()

    return db_item  # 回傳被刪除的資料


# 刪除子選單
@nav_router.delete("/deleteNav1/{item_id}", response_model=NavDropdownRead)
def delete_nav_item(
    item_id: int,
    nav_item_create: NavDropdownCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    print("deleteNav1")
    db_item = (
        db.query(NavDropdown)
        .filter(
            NavDropdown.id == item_id,
            NavDropdown.nav_item_id == nav_item_create.nav_item_id,
        )
        .first()
    )
    if not db_item:
        raise HTTPException(status_code=404, detail="NavItem not found")

    db.delete(db_item)
    db.commit()

    return db_item  # 回傳被刪除的資料
