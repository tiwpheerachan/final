import time
import hashlib
import hmac
import requests
import os

PARTNER_ID = os.getenv("PARTNER_ID")
PARTNER_KEY = os.getenv("PARTNER_KEY")
REDIRECT_URL = os.getenv("REDIRECT_URL")

def generate_auth_url():
    base_url = "https://partner.shopeemobile.com/api/v2/shop/auth_partner"
    timestamp = int(time.time())

    data_to_sign = f"{PARTNER_ID}{REDIRECT_URL}{timestamp}"
    sign = hmac.new(PARTNER_KEY.encode(), data_to_sign.encode(), hashlib.sha256).hexdigest()

    return f"{base_url}?partner_id={PARTNER_ID}&timestamp={timestamp}&sign={sign}&redirect={REDIRECT_URL}"

def exchange_token(code, shop_id):
    url = "https://partner.shopeemobile.com/api/v2/auth/token/get"
    timestamp = int(time.time())
    path = "/api/v2/auth/token/get"
    base_string = f"{PARTNER_ID}{path}{timestamp}"
    sign = hmac.new(PARTNER_KEY.encode(), base_string.encode(), hashlib.sha256).hexdigest()

    res = requests.post(url, json={
        "code": code,
        "partner_id": int(PARTNER_ID),
        "shop_id": int(shop_id)
    }, headers={
        "Content-Type": "application/json",
        "Authorization": sign,
        "timestamp": str(timestamp)
    })

    return res.json()
