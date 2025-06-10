import os
import psycopg2
from dotenv import load_dotenv

# โหลดตัวแปรจากไฟล์ .env
load_dotenv()

# ดึงค่าตัวแปรจาก .env
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# ฟังก์ชันสำหรับเชื่อมต่อฐานข้อมูล
def get_connection():
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=int(DB_PORT),
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            sslmode='require'  # สำหรับ Supabase ให้ใส่ sslmode ด้วย
        )
        return conn
    except Exception as e:
        print("❌ ไม่สามารถเชื่อมต่อฐานข้อมูลได้:", e)
        return None

# ทดสอบการเชื่อมต่อ
if __name__ == "__main__":
    conn = get_connection()
    if conn:
        with conn.cursor() as cur:
            cur.execute("SELECT NOW();")
            now = cur.fetchone()
            print("✅ เชื่อมต่อสำเร็จ! เวลาปัจจุบันจากฐานข้อมูล:", now)
        conn.close()
