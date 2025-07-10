from fastapi import APIRouter, Depends, HTTPException, Body
from typing import List
from lib_db.db.database import get_db  # 你定義的 get_db function

from lib_sql.sql_loader_singleton import get_sql_loader
from lib_sql.SQLQueryExecutor import SQLQueryExecutor
from lib_db.db.database import get_async_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

db_create_router = APIRouter(prefix="/DBCreate", tags=["DBCreate"])
sql_loader = get_sql_loader()


@db_create_router.post("/TABLE_INSERT/{sql_key}")
async def insert_post(
    sql_key: str, payload: dict = Body(...), db: AsyncSession = Depends(get_async_db)
):
    print("Table insert")
    print(f"SQL Key: {sql_key}")
    print(f"Payload: {payload}")
    try:
        executor = SQLQueryExecutor(sql_loader, db)
        result = await executor.execute(sql_key, payload)
        return result
    except Exception as e:
        raise e


# 將 角色 ID 填入 nav_item_roles , nav_drop_roles
@db_create_router.post("/TABLE_INSERT_M/{sql_key}")
async def insert_m_post(
    sql_key: str, payload: dict = Body(...), db: AsyncSession = Depends(get_async_db)
):
    print("Table insert M")
    print(f"SQL Key: {sql_key}")
    try:
        print(payload)
        # 驗證 payload 結構
        if not isinstance(payload, dict):
            raise HTTPException(status_code=400, detail="Invalid payload format")

        if "menu_items" not in payload:
            raise HTTPException(
                status_code=400, detail="Missing 'menu_items' in payload"
            )

        if "role_id" not in payload:
            raise HTTPException(status_code=400, detail="Missing 'role_id' in payload")

        menu_items = payload["menu_items"]
        role_id = payload["role_id"]

        # 獲取 SQL 語句
        sqldeleteMain = sql_loader.get_sql("DELETE_NAV_ITEM_ROLES")
        sqldeleteDrop = sql_loader.get_sql("DELETE_NAV_DROPDOWN_ROLES")

        sqlmain = sql_loader.get_sql("INSERT_NAV_ITEM_ROLES")
        sqlsub = sql_loader.get_sql("INSERT_NAV_DROPDOWN_ROLES")

        # 轉換為 SQLAlchemy text 對象
        sql_delete_main = text(sqldeleteMain)
        sql_delete_drop = text(sqldeleteDrop)

        sql_insert_main = text(sqlmain)
        sql_insert_sub = text(sqlsub)

        print(f"Deleting records for role_id: {role_id}")

        # 在同一個事務中執行所有操作
        # 1. 先刪除現有記錄
        await db.execute(sql_delete_main, {"role_id": role_id})
        await db.execute(sql_delete_drop, {"role_id": role_id})

        print("Delete operations completed")

        # 2. 插入新記錄
        for i, item in enumerate(menu_items):
            # 驗證 item 結構
            if not isinstance(item, dict):
                raise HTTPException(
                    status_code=400, detail=f"Invalid item format at index {i}"
                )

            if "id" not in item or "type" not in item:
                raise HTTPException(
                    status_code=400,
                    detail=f"Missing 'id' or 'type' in item at index {i}",
                )

            item_id = item["id"]
            item_type = item["type"]

            if item_type == "0":
                await db.execute(
                    sql_insert_main, {"nav_item_id": item_id, "role_id": role_id}
                )
                print(f"Inserted nav_item_id: {item_id} for role_id: {role_id}")
            elif item_type == "1":
                await db.execute(
                    sql_insert_sub, {"nav_dropdown_id": item_id, "role_id": role_id}
                )
                print(f"Inserted nav_dropdown_id: {item_id} for role_id: {role_id}")
            else:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid item type: {item_type} at index {i}",
                )

        # 3. 只在最後提交一次事務
        await db.commit()
        print("All operations committed successfully")

        return {"status": "success", "inserted": len(menu_items)}

    except HTTPException:
        await db.rollback()
        print("Transaction rolled back due to HTTPException")
        raise

    except Exception as e:
        await db.rollback()
        print(f"Transaction rolled back due to error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
