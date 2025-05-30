import requests
import psycopg2
import os
import time
from dotenv import load_dotenv

load_dotenv()

# ------------------ DB Connect ------------------ #
conn = psycopg2.connect(
    host=os.getenv("SUPABASE_HOST"),
    port=os.getenv("SUPABASE_PORT"),
    dbname=os.getenv("SUPABASE_DBNAME"),
    user=os.getenv("SUPABASE_USER"),
    password=os.getenv("SUPABASE_PASSWORD")
)
cursor = conn.cursor()

# ------------------ Shopee Mock Fetch ------------------ #
def fetch_shopee_orders():
    # ปกติจะใช้ requests.post กับ Shopee API จริง
    # นี่เป็น mock JSON จำลองตัวอย่าง
    return [
        {
            "order_id": "123456789",
            "buyer_username": "buyer001",
            "total_amount": 299.0,
            "order_status": "COMPLETED"
        },
        {
            "order_id": "987654321",
            "buyer_username": "buyer002",
            "total_amount": 159.0,
            "order_status": "READY_TO_SHIP"
        }
    ]

# ------------------ Insert to Supabase ------------------ #
def insert_orders_to_db(orders):
    for order in orders:
        cursor.execute("""
            INSERT INTO orders (order_id, buyer_username, total_amount, order_status)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (order_id) DO NOTHING
        """, (
            order["order_id"],
            order["buyer_username"],
            order["total_amount"],
            order["order_status"]
        ))
    conn.commit()
    print(f"✅ Inserted {len(orders)} orders")

# ------------------ Refresh Loop ------------------ #
def refresh_loop(interval=30):
    while True:
        print("🔄 Fetching data from Shopee...")
        orders = fetch_shopee_orders()
        insert_orders_to_db(orders)
        time.sleep(interval)

if __name__ == "__main__":
    refresh_loop()
