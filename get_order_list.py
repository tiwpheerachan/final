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

    shop_id = str(shop_id).strip()  # ✅ ป้องกันปัญหาความผิดพลาด
    base_string = f"{PARTNER_ID}{path}{timestamp}{access_token}{shop_id}"
    sign = hmac.new(PARTNER_KEY.encode(), base_string.encode(), hashlib.sha256).hexdigest()

    url = (
        f"{BASE_URL}{path}"
        f"?partner_id={PARTNER_ID}"
        f"&timestamp={timestamp}"
        f"&access_token={access_token}"
        f"&shop_id={shop_id}"
        f"&sign={sign}"
    )

    payload = {
        "time_range_field": "create_time",
        "time_from": timestamp - time_gap_seconds,
        "time_to": timestamp,
        "page_size": 20,
        "order_status": "ALL"
    }

    headers = {"Content-Type": "application/json"}
    response = requests.post(url, json=payload, headers=headers)
    return response.json()
