from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import asc

from lib_db.db.database import SessionLocal
from lib_db.models.nav_item import NavItem
from lib_db.models.nav_dropdown import NavDropdown
from lib_db.models.role import Role
from lib_db.schemas.nav import NavItemCreate, NavItemRead, NavItemUpdate
from lib_db.schemas.nav import NavDropdownCreate, NavDropdownRead, NavDropdownUpdate
from sqlalchemy.ext.asyncio import AsyncSession

# from lib_db.schemas.nav import NavItemRoleLinkCreate

from typing import List


from lib_sql.SQLQueryExecutor import SQLQueryExecutor

from lib_util.Auth import get_current_user, get_optional_user  # Import the dependency
from lib_db.models.User import User

from lib_db.db.database import get_async_db
from lib_sql.sql_loader_singleton import get_sql_loader
from sqlalchemy import text
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from lib_db.db.database import get_db  # 你的資料庫依賴
import logging


nav_router = APIRouter(prefix="/nav", tags=["Navigation"])


sql_loader = get_sql_loader()  # SQL 字典
logger = logging.getLogger(__name__)


# nav_router = APIRouter()
nav_router = APIRouter(prefix="/nav", tags=["Navigation"])
logger = logging.getLogger(__name__)


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


# 更新主選單
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
@nav_router.post("/createNav0_OLD", response_model=NavItemRead)
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


# 新增主選單
@nav_router.post("/createNav0")
async def create_nav_item(
    request: Request,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    # body = await request.json()
    try:
        body = await request.json()
        executor = SQLQueryExecutor(sql_loader, db)
        result = await executor.execute(
            "INSERT_NAV_ITEMS", body
        )  # 增加主選單 取得 inserted_id : result.inserted_id
        # 增加到
        return result
    except Exception as e:

        raise HTTPException(status_code=500, detail=str(e))


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


# 刪除主選單
@nav_router.delete("/deleteNav0/{item_id}", response_model=NavItemRead)
def delete_nav_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_item = db.query(NavItem).filter(NavItem.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="NavItem not found")
    db.delete(db_item)
    db.commit()
    return db_item  # 回傳被刪除的資料


# 刪除子選單 current_user: User = Depends(get_current_user), 正常運作就不要改了
@nav_router.delete("/deleteNav1/{item_id}", response_model=NavDropdownRead)
async def delete_nav_item(
    item_id: int,
    nav_item_create: NavDropdownCreate,
    db: Session = Depends(get_db),
    dbasync: Session = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    # print(current_user)
    # print("deleteNav1")
    # print(item_id)
    # print(nav_item_create.nav_item_id)
    # sql = sql_loader.get_sql("SELECT_NAV_DROPDOWNS_NAVID_ID")
    # print(sql)
    # parms = {"nav_item_id": int(nav_item_create.nav_item_id), "id": int(item_id)}
    # executor = SQLQueryExecutor(sql_loader, dbasync)
    # rs = await executor.execute("SELECT_NAV_DROPDOWNS_NAVID_ID", parms)
    # print(rs)

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


# 使用 RoleID 取得 Menu 只有 Super Admin 可以使用
def getNavLinksByRoleID(db, role_id):
    raw_sql = sql_loader.get_sql("SELECT_MENU_BY_ROLE_ID")

    result = db.execute(text(raw_sql), {"role_id": role_id})
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


# 取得 menu 預設角色為 6
@nav_router.get("/links")
def get_nav_links(
    db: Session = Depends(get_db), current_user: User = Depends(get_optional_user)
):  # 改用 get_db 而非 get_async_db
    logger.info("使用純 SQL 查詢 nav_items + nav_dropdowns")
    try:

        role_id = 6
        if current_user is not None:
            role_id = current_user.role_id

        logger.info("取得目前使用者的角色")
        logger.info(role_id)
        nav_items = []
        nav_items = getNavLinksByRoleID(db, role_id)

        return nav_items

    except SQLAlchemyError as e:
        logger.error(f"SQLAlchemy error in get_nav_links: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error")
    except Exception as e:
        logger.error(f"Unexpected error in get_nav_links: {str(e)}")
        raise HTTPException(status_code=500, detail="Unexpected error")


# 標註是否選取
def mark_selected(nav_items_all, nav_items_selected):
    def find_match(item, selected_items):
        for sel in selected_items:
            if item["id"] == sel["id"]:
                return sel
        return None

    for item in nav_items_all:
        match = find_match(item, nav_items_selected)
        item["is_selected"] = True if match else False

        # dropdown 比對
        all_dropdowns = item.get("dropdown", [])
        selected_dropdowns = match.get("dropdown", []) if match else []

        for dropdown in all_dropdowns:
            dropdown_match = next(
                (d for d in selected_dropdowns if d["id"] == dropdown["id"]), None
            )
            dropdown["is_selected"] = True if dropdown_match else False

    return nav_items_all


# 使用角色取得 menu
@nav_router.get("/qyerLinkbyRoleId/{role_id}")
async def get_nav_links(
    role_id: int,  # 👈 這樣 Swagger 才會出現輸入欄位
    dbasync: Session = Depends(get_async_db),
    db: Session = Depends(get_db),
):  # 改用 get_db 而非 get_async_db
    """使用Role_id 查詢 Menu"""
    try:
        logger.info("取得目前使用者的角色", "SELECT_ALL_MENU")
        #
        executor = SQLQueryExecutor(sql_loader, dbasync)
        result = await executor.execute("SELECT_ALL_MENU")
        #
        role_id = role_id
        nav_items = []
        nav_items = getNavLinksByRoleID(db, role_id)
        # 標註是否選取
        nav_items_all = mark_selected(result, nav_items)
        return nav_items_all

    except SQLAlchemyError as e:
        logger.error(f"SQLAlchemy error in get_nav_links: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error")
    except Exception as e:
        logger.error(f"Unexpected error in get_nav_links: {str(e)}")
        raise HTTPException(status_code=500, detail="Unexpected error")


# 取得所有的 menu 不使用 role_id 當選擇條件
@nav_router.get("/allmenus")
async def get_allmenus(
    db: AsyncSession = Depends(get_async_db),
):
    try:
        executor = SQLQueryExecutor(sql_loader, db)
        result = await executor.execute("SELECT_ALL_MENU")
        # 增加到
        return result

    except Exception as e:
        print(f"🔥 Error at line: {e.__traceback__.tb_lineno}")
        print(f"🔥 Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
