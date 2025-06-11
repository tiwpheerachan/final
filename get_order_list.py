# ✅ get_order_list.py
import time, hmac, hashlib, os, requests
from dotenv import load_dotenv
load_dotenv()

def get_order_list():
    path = "/api/v2/order/get_order_list"
    partner_id = os.getenv("PARTNER_ID")
    partner_key = os.getenv("PARTNER_KEY")
    access_token = os.getenv("ACCESS_TOKEN")
    shop_id = os.getenv("SHOP_ID")
    timestamp = int(time.time())

    base_string = f"{partner_id}{path}{timestamp}{access_token}{shop_id}"
    sign = hmac.new(partner_key.encode(), base_string.encode(), hashlib.sha256).hexdigest()

    url = (
        f"https://partner.shopeemobile.com{path}?"
        f"partner_id={partner_id}&timestamp={timestamp}"
        f"&access_token={access_token}&shop_id={shop_id}&sign={sign}"
    )

    payload = {
        "time_range_field": "create_time",
        "page_size": 10,
        "order_status": "COMPLETED",
        "create_time_from": int(time.time()) - 86400,
        "create_time_to": int(time.time())
    }

    response = requests.post(url, json=payload)
    return response.json()
