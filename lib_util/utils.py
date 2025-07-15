# 使用者 ID 格式化 建立使用者目錄使用
def format_user_id(user_id: int, length: int = 10) -> str:
    return str(user_id).zfill(length)


def parse_user_id(padded_id: str) -> int:
    return int(padded_id.lstrip("0") or "0")
