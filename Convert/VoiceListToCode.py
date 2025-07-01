import sys
import os

# 把根目錄加入 sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy.orm import Session
from lib_db.schemas.Code import CodeCreate
from lib_services.code_service import CodeService
from lib_db.db.database import SessionLocal


def import_voices_from_txt(file_path: str, db: Session):
    service = CodeService(db)
    print(file_path)  # 這行現在會執行了

    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for line in lines:
        print(line)
        # 使用固定寬度解析
        voice_id = line[0:35].strip()
        gender = line[35:45].strip()
        style = line[45:75].strip()
        tone = line[75:].strip()

        description = f"{style} - {tone}"

        code_data = CodeCreate(
            category="voice",
            code=voice_id,
            name=gender,
            description=description,
            sort_order=0,
            is_active=1,
        )

        try:
            service.create(code_data)
            print(f"✅ 新增成功：{voice_id}")
        except Exception as e:
            print(f"❌ 新增失敗：{voice_id} → {str(e)}")


def main():
    db = SessionLocal()
    try:
        file_path = "c:/temp/aa.txt"  # 路徑可調整
        import_voices_from_txt(file_path, db)
    finally:
        db.close()


# 加上這段才會執行 main()
if __name__ == "__main__":
    main()
