from shopee_fetcher import get_order_list
from shopee_to_supabase import (
    insert_order_detail_to_supabase,
    insert_order_items,
    insert_income_to_supabase,
    insert_shop_info,
    insert_product_to_supabase
)
from get_order_detail import get_order_detail

import time

def refresh_loop():
    print("🔄 Starting Shopee data sync...")

    try:
        order_data = get_order_list().get("response", {}).get("order_list", [])
        for order in order_data:
            order_sn = order["order_sn"]
            print(f"📦 Syncing order: {order_sn}")
            insert_order_detail_to_supabase(order_sn)
            insert_order_items(order_sn)
            insert_income_to_supabase(order_sn)

        print("🏬 Syncing shop info...")
        insert_shop_info()

        print("🛒 Syncing product info from recent items...")
        for order in order_data:
            detail = get_order_detail(order["order_sn"]).get("response", {})
            for item in detail.get("item_list", []):
                item_id = item["item_id"]
                insert_product_to_supabase(item_id)

        print("✅ Sync completed.")

    except Exception as e:
        print(f"❌ Sync failed: {e}")

if __name__ == "__main__":
    refresh_loop()