from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse
from lib_util.CGrammar import GrammarChecker
from pydantic import BaseModel

util_router = APIRouter()
util_router = APIRouter(
    prefix="/utils",
    tags=["utils"],
)


class GrammarRequest(BaseModel):
    text: str


@util_router.post(
    "/grammarcheck",
)
async def check(request: GrammarRequest):
    checker = GrammarChecker()
    result = checker.check(request.text)
    return result
