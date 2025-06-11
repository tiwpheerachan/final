import os
import time
import psycopg2
from dotenv import load_dotenv
from supabase import create_client
from get_order_list import get_order_list  # ✅ ตรวจสอบให้ตรงชื่อไฟล์จริง

# ✅ โหลด .env
load_dotenv()

# ✅ ตั้งค่า Supabase SDK
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

# ✅ ดึง access_token + shop_id ล่าสุด
def get_latest_token():
    try:
        result = supabase.table("shopee_tokens").select("*").order("last_updated", desc=True).limit(1).execute()
        row = result.data[0]
        return row["access_token"], row["shop_id"]
    except Exception as e:
        print("❌ Error loading token:", e)
        return None, None

# ✅ เชื่อมต่อ Supabase DB
def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )

# ✅ ดึงคำสั่งซื้อจาก Shopee API
def fetch_shopee_orders():
    access_token, shop_id = get_latest_token()
    if not access_token or not shop_id:
        print("❌ Missing access_token or shop_id")
        return []

    try:
        response = get_order_list(access_token=access_token, shop_id=shop_id, time_gap_seconds=86400)
        if response.get("error"):
            print(f"❌ API Error: {response['error']}")
            return []
        return response.get("response", {}).get("order_list", [])
    except Exception as e:
        print("❌ Error fetching orders:", e)
        return []

# ✅ บันทึกข้อมูลลง Supabase Table
def insert_orders_to_db(orders):
    if not orders:
        print("⚠️ No orders to insert.")
        return

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        for order in orders:
            cursor.execute("""
                INSERT INTO orders (order_sn, shop_id, region, currency, cod, order_status, create_time, update_time)
                VALUES (%s, %s, %s, %s, %s, %s, to_timestamp(%s), to_timestamp(%s))
                ON CONFLICT (order_sn) DO NOTHING;
            """, (
                order["order_sn"],
                order.get("shop_id"),
                order.get("region"),
                order.get("currency"),
                order.get("cod", False),
                order.get("order_status"),
                order.get("create_time"),
                order.get("update_time")
            ))

        conn.commit()
        cursor.close()
        conn.close()
        print(f"✅ Inserted {len(orders)} orders into Supabase")

    except Exception as e:
        print("❌ Error inserting into DB:", e)

# ✅ เรียกใช้เมื่อ run script
if __name__ == "__main__":
    orders = fetch_shopee_orders()
    insert_orders_to_db(orders)
