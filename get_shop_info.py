import os
import time
import hmac
import hashlib
import requests

def get_shop_info():
    path = "/api/v2/shop/get_shop_info"
    partner_id = os.getenv("PARTNER_ID")
    partner_key = os.getenv("PARTNER_KEY")
    access_token = os.getenv("ACCESS_TOKEN")
    shop_id = os.getenv("SHOP_ID")
    timestamp = int(time.time())

    base_string = f"{partner_id}{path}{timestamp}{access_token}{shop_id}"
    sign = hmac.new(partner_key.encode(), base_string.encode(), hashlib.sha256).hexdigest()

    url = f"https://partner.shopeemobile.com{path}?partner_id={partner_id}&timestamp={timestamp}&access_token={access_token}&shop_id={shop_id}&sign={sign}"
    res = requests.get(url)
    return res.json()