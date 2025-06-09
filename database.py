from dotenv import load_dotenv
import os
import psycopg2

# โหลดค่าจากไฟล์ .env
load_dotenv()

# ดึงค่าจาก .env
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# ฟังก์ชันเชื่อมต่อฐานข้อมูล
def get_connection():
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        return conn
    except Exception as e:
        print("❌ เชื่อมต่อฐานข้อมูลไม่สำเร็จ:", e)
        return None

# ✅ ทดสอบการเชื่อมต่อฐานข้อมูล
if __name__ == "__main__":
    conn = get_connection()
    if conn:
        cur = conn.cursor()
        cur.execute("SELECT NOW();")
        print("✅ เวลาปัจจุบันจากฐานข้อมูล:", cur.fetchone())
        cur.close()
        conn.close()
