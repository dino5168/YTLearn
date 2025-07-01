import psycopg2

DATABASE_URL = "postgresql://postgres:0936284791@localhost:5432/videos"

try:
    conn = psycopg2.connect(DATABASE_URL)
    print("✅ 連線成功！")
    conn.close()
except Exception as e:
    print("❌ 連線失敗:", e)
