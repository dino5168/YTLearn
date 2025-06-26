# backend/routes/nav.py
from fastapi import APIRouter

nav_router = APIRouter(prefix="/nav", tags=["Navigation"])


@nav_router.get("/links")
def get_nav_links():
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
        {"label": "登入", "href": "/auth/Login"},
    ]
