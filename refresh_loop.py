from shopee_fetcher import get_order_list
from shopee_to_supabase import insert_orders_to_supabase
import time

def refresh_loop():
    print("🔄 Starting refresh...")
    orders = get_order_list()
    insert_orders_to_supabase(orders)
    print("✅ Sync completed.")

if __name__ == "__main__":
    refresh_loop()  # รันทันที ถ้าเอาไปใช้กับ cron job
