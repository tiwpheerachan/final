import os, time, hmac, hashlib, requests
from dotenv import load_dotenv
load_dotenv()

BASE_URL = "https://partner.shopeemobile.com"
PARTNER_ID = os.getenv("PARTNER_ID")
PARTNER_KEY = os.getenv("PARTNER_KEY")

def get_item_list(access_token, shop_id):
    path = "/api/v2/product/get_item_list"
    timestamp = int(time.time())
    base_string = f"{PARTNER_ID}{path}{timestamp}{access_token}{shop_id}"
    sign = hmac.new(PARTNER_KEY.encode(), base_string.encode(), hashlib.sha256).hexdigest()

    url = (
        f"{BASE_URL}{path}?partner_id={PARTNER_ID}"
        f"&timestamp={timestamp}&access_token={access_token}&shop_id={shop_id}&sign={sign}"
    )

    item_list = []
    offset = 0

    while True:
        params = {"offset": offset, "page_size": 50}
        response = requests.get(url, params=params)
        data = response.json()

        if "item" in data:
            item_list += data["item"]
            if not data.get("has_next_page", False):
                break
            offset += 50
        else:
            break

    return item_list
