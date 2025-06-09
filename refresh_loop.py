import os
import time
from dotenv import load_dotenv

from shopee_fetcher import get_order_list
from get_order_detail import get_order_detail
from shopee_to_supabase import (
    insert_order_detail_to_supabase,
    insert_order_items,
    insert_income_to_supabase,
    insert_shop_info,
    insert_product_to_supabase
)

# 🔐 โหลดค่า ENV เช่น access_token, shop_id
load_dotenv()
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
SHOP_ID = os.getenv("SHOP_ID")

def refresh_loop():
    print("🔄 Starting Shopee data sync...")

    try:
        # ✅ STEP 1: ดึงรายการคำสั่งซื้อ
        print("📥 Fetching order list...")
        order_response = get_order_list(ACCESS_TOKEN, SHOP_ID)
        order_data = order_response.get("response", {}).get("order_list", [])

        if not order_data:
            print("⚠️ No orders found.")
            return

        # ✅ STEP 2: วนลูป order และดึงรายละเอียด
        for order in order_data:
            order_sn = order["order_sn"]
            print(f"📦 Syncing order: {order_sn}")

            try:
                insert_order_detail_to_supabase(order_sn)
                insert_order_items(order_sn)
                insert_income_to_supabase(order_sn)

                # ✅ STEP 3: ดึง item ใน order ไป insert สินค้า
                detail = get_order_detail(order_sn, ACCESS_TOKEN, SHOP_ID).get("response", {})
                for item in detail.get("item_list", []):
                    item_id = item["item_id"]
                    insert_product_to_supabase(item_id)

            except Exception as inner_e:
                print(f"❌ Failed to sync order {order_sn}: {inner_e}")

        # ✅ STEP 4: Sync ข้อมูลร้านค้า
        print("🏬 Syncing shop info...")
        insert_shop_info(ACCESS_TOKEN, SHOP_ID)

        print("✅ Shopee sync completed.")

    except Exception as e:
        print(f"❌ Sync failed: {e}")

if __name__ == "__main__":
    refresh_loop()
