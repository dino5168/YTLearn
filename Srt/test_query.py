import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)
import csv
from sqlalchemy.orm import Session
from lib_db.db.database import get_db
from lib_db.models.Subtitle import Subtitle
from lib_db.models.Code import Code
from typing import Type, List


def get_data_by_class(model_class: Type, limit: int = 100) -> List:
    db_gen = get_db()
    db: Session = next(db_gen)
    try:
        query = db.query(model_class)
        if limit:
            query = query.limit(limit)
        return query.all()
    except:
        print("exception")
    finally:
        db.close()


def write_data_csv(outputfn: str, dataList: List[object]) -> bool:
    try:
        if not dataList:
            print("no data")
            return False  # 沒資料就不寫

        # 自動取得欄位名稱（假設是 ORM 或有 __dict__ 的物件）
        fieldnames = dataList[0].__table__.columns.keys()  # 適用 SQLAlchemy ORM

        with open(outputfn, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for item in dataList:
                writer.writerow({k: getattr(item, k) for k in fieldnames})

        return True
    except Exception as e:
        print(f"寫入失敗: {e}")
        return False


def hello():
    dataList = get_data_by_class(Code)
    for col in Code.__table__.columns:
        print(col.name)

    isOK = write_data_csv("c:/temp/Code.csv", dataList)
    print(isOK)


if __name__ == "__main__":
    hello()
