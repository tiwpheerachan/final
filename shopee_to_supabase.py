import os
import time
import psycopg2
from dotenv import load_dotenv
from shopee_fetcher import get_order_list

# ✅ โหลด environment variables
load_dotenv()

# ------------------ Shopee Auth ------------------ #
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
SHOP_ID = os.getenv("SHOP_ID")

# ------------------ Connect to Supabase PostgreSQL ------------------ #
def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )

# ------------------ Fetch Shopee Orders ------------------ #
def fetch_shopee_orders():
    try:
        response = get_order_list(
            access_token=ACCESS_TOKEN,
            shop_id=SHOP_ID,
            time_gap_seconds=3600
        )
        if response.get("error"):
            print(f"❌ Shopee API Error: {response['message']}")
            return []
        return response.get("response", {}).get("order_list", [])
    except Exception as e:
        print("❌ Error fetching orders:", e)
        return []

# ------------------ Insert Orders to Supabase ------------------ #
def insert_orders_to_db(orders):
    if not orders:
        print("⚠️ No orders to insert.")
        return

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        for order in orders:
            cursor.execute("""
                INSERT INTO orders (order_id, buyer_username, total_amount, order_status)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (order_id) DO NOTHING
            """, (
                order["order_sn"],
                order.get("buyer_username", "unknown"),
                float(order.get("total_amount", 0)),
                order.get("order_status", "unknown")
            ))

        conn.commit()
        cursor.close()
        conn.close()
        print(f"✅ Inserted {len(orders)} orders into Supabase")

    except Exception as e:
        print("❌ Error inserting into DB:", e)

# ------------------ Optional Loop (if not using cron) ------------------ #
def refresh_loop(interval=1800):
    while True:
        print("🔄 Fetching Shopee orders...")
        orders = fetch_shopee_orders()
        insert_orders_to_db(orders)
        time.sleep(interval)

# ✅ เรียกใช้ครั้งเดียว (ใช้ใน Cron job)
if __name__ == "__main__":
    orders = fetch_shopee_orders()
    insert_orders_to_db(orders)
