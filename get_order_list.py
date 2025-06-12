import time
import hmac
import hashlib
import os
import requests
from dotenv import load_dotenv

# ✅ Load env
load_dotenv()

BASE_URL = "https://partner.shopeemobile.com"
PARTNER_ID = os.getenv("PARTNER_ID")
PARTNER_KEY = os.getenv("PARTNER_KEY")

assert PARTNER_ID and PARTNER_KEY, "Missing Shopee credentials"

def get_order_list(access_token, shop_id, time_gap_seconds=86400):
    path = "/api/v2/order/get_order_list"
    timestamp = int(time.time())

    # ✅ shop_id ต้องเป็น int ใน base_string
    shop_id_int = int(shop_id)

    base_string = f"{PARTNER_ID}{path}{timestamp}{access_token}{shop_id_int}"
    sign = hmac.new(PARTNER_KEY.encode(), base_string.encode(), hashlib.sha256).hexdigest()

    params = {
        "partner_id": PARTNER_ID,
        "timestamp": timestamp,
        "access_token": access_token,
        "shop_id": shop_id_int,
        "sign": sign,
        "time_range_field": "create_time",
        "time_from": timestamp - time_gap_seconds,
        "time_to": timestamp,
        "page_size": 20,
        "order_status": "ALL"
    }

    url = f"{BASE_URL}{path}"
    response = requests.get(url, params=params)
    return response.json()
