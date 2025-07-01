import psycopg2
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# PostgreSQL 連線字串格式:
# postgresql://<username>:<password>@<host>:<port>/<database_name>
# DATABASE_URL = "postgresql://dino:0936284791@localhost:5432/videos"
DATABASE_URL = "postgresql://postgres:0936284791@localhost:5432/videos"

engine = create_engine(DATABASE_URL, pool_pre_ping=True)  # 連線池檢查連線有效性

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
