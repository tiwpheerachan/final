import hashlib
import hmac
import time
import requests
import os

# ✅ โหลดค่าจาก ENV
PARTNER_ID = os.getenv("PARTNER_ID") or "2011520"
PARTNER_KEY = os.getenv("PARTNER_KEY") or "707378444d6c6652564a427658499647f7617a4f6a75487069547745746e6b4b"
BASE_URL = "https://partner.shopeemobile.com"  

def make_signature(partner_id, path, timestamp, access_token, shop_id, partner_key):
    base_string = f"{partner_id}{path}{timestamp}{access_token}{shop_id}"
    return hmac.new(
        partner_key.encode("utf-8"),
        base_string.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()

def get_order_list(access_token: str, shop_id: int, time_gap_seconds: int = 3600):
    """
    ✅ ดึงรายการคำสั่งซื้อจาก Shopee ด้วย access_token และ shop_id
    """
    path = "/api/v2/order/get_order_list"
    timestamp = int(time.time())
    sign = make_signature(PARTNER_ID, path, timestamp, access_token, shop_id, PARTNER_KEY)

    # ✅ Shopee API URL
    url = (
        f"{BASE_URL}{path}"
        f"?partner_id={PARTNER_ID}"
        f"&timestamp={timestamp}"
        f"&access_token={access_token}"
        f"&shop_id={shop_id}"
        f"&sign={sign}"
    )

    # ✅ Payload JSON ใน POST (ไม่ใช่ query params)
    payload = {
        "time_range_field": "create_time",
        "time_from": timestamp - time_gap_seconds,
        "time_to": timestamp,
        "page_size": 50
    }

    headers = {"Content-Type": "application/json"}
    response = requests.post(url, json=payload, headers=headers)

    try:
        return response.json()
    except Exception:
        return {
            "error": "Invalid JSON response",
            "status_code": response.status_code,
            "text": response.text
        }
