# routers/markdown.py
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from lib_db.db.database import get_async_db
from pathlib import Path
from app.config import settings

markdown_router = APIRouter(prefix="/markdown", tags=["markdown"])

# 假設 markdown 存放於此資料夾
MARKDOWN_BASE_DIR = settings.MARK_DOWN_DIR


@markdown_router.get("/")
async def get_markdown_file(
    file: str = Query(..., description="Markdown 檔案名稱，例如：001.md"),
    db: AsyncSession = Depends(get_async_db),
):
    file_path = MARKDOWN_BASE_DIR / file

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="檔案不存在")

    if not file_path.suffix == ".md":
        raise HTTPException(status_code=400, detail="只支援 .md 檔案")

    content = file_path.read_text(encoding="utf-8")

    return {"filename": file, "markdown": content}
