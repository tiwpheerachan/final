# 📁 get_order_detail.py
import time
import hmac
import hashlib
import os
import requests
from dotenv import load_dotenv

load_dotenv()

# ✅ รับ parameter แบบ dynamic เพื่อใช้กับ refresh_loop
def get_order_detail(order_sn, access_token=None, shop_id=None):
    path = "/api/v2/order/get_order_detail"
    partner_id = os.getenv("PARTNER_ID") or "2011520"
    partner_key = os.getenv("PARTNER_KEY") or "707378444d6c6652564a427658499647f7617a4f6a75487069547745746e6b4b"

    # ✅ fallback ถ้ายังไม่มีค่า
    access_token = access_token or os.getenv("ACCESS_TOKEN")
    shop_id = shop_id or os.getenv("SHOP_ID")

    timestamp = int(time.time())
    base_string = f"{partner_id}{path}{timestamp}{access_token}{shop_id}"
    sign = hmac.new(partner_key.encode(), base_string.encode(), hashlib.sha256).hexdigest()

    url = (
        f"https://partner.shopeemobile.com{path}"
        f"?partner_id={partner_id}"
        f"&timestamp={timestamp}"
        f"&access_token={access_token}"
        f"&shop_id={shop_id}"
        f"&sign={sign}"
    )

    try:
        res = requests.post(url, json={"order_sn": order_sn})
        res.raise_for_status()
        return res.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Error calling get_order_detail: {e}")
        return {"error": "request_failed", "message": str(e)}
