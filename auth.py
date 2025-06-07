import time
import hashlib
import hmac
import requests
import os

# โหลด ENV
PARTNER_ID = os.getenv("PARTNER_ID")
PARTNER_KEY = os.getenv("PARTNER_KEY")
REDIRECT_URL = os.getenv("REDIRECT_URL")

# ✅ 1. ใช้ URL ที่ตรงกับ Sandbox
AUTH_BASE_URL = "https://partner.test-stable.shopeemobile.com"

def generate_auth_url():
    base_url = "https://partner.test-stable.shopeemobile.com/api/v2/shop/auth_partner"
    timestamp = int(time.time())
    path = "/api/v2/shop/auth_partner"
    
    base_string = f"{PARTNER_ID}{path}{timestamp}"
    sign = hmac.new(PARTNER_KEY.encode(), base_string.encode(), hashlib.sha256).hexdigest()

    return f"{base_url}?partner_id={PARTNER_ID}&timestamp={timestamp}&sign={sign}&redirect={REDIRECT_URL}"

def exchange_token(code, shop_id):
    """แลกรับ Access Token ด้วย code + shop_id"""
    path = "/api/v2/auth/token/get"
    timestamp = int(time.time())

    base_string = f"{PARTNER_ID}{path}{timestamp}"
    sign = hmac.new(PARTNER_KEY.encode(), base_string.encode(), hashlib.sha256).hexdigest()

    url = f"{AUTH_BASE_URL}{path}?partner_id={PARTNER_ID}&timestamp={timestamp}&sign={sign}"

    payload = {
        "code": code,
        "partner_id": int(PARTNER_ID),
        "shop_id": int(shop_id)
    }

    headers = {
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)
    return response.json()
