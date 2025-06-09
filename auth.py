import time
import hashlib
import hmac
import requests
import os

# ✅ โหลด ENV ค่าจริงสำหรับ Production
PARTNER_ID = os.getenv("PARTNER_ID") or "2011520"
PARTNER_KEY = os.getenv("PARTNER_KEY") or "707378444d6c6652564a427658499647f7617a4f6a75487069547745746e6b4b"
REDIRECT_URL = os.getenv("REDIRECT_URL") or "https://final-e74d.onrender.com/callback"

# ✅ ใช้ Production Base URL
AUTH_BASE_URL = "https://partner.shopeemobile.com"

def generate_auth_url():
    """
    ✅ Step 1: สร้างลิงก์สำหรับ Shopee OAuth Login
    """
    path = "/api/v2/shop/auth_partner"
    timestamp = int(time.time())
    base_string = f"{PARTNER_ID}{path}{timestamp}"

    sign = hmac.new(PARTNER_KEY.encode(), base_string.encode(), hashlib.sha256).hexdigest()

    url = (
        f"{AUTH_BASE_URL}{path}"
        f"?partner_id={PARTNER_ID}"
        f"&timestamp={timestamp}"
        f"&sign={sign}"
        f"&redirect={REDIRECT_URL}"
    )
    return url

def exchange_token(code, shop_id):
    """
    ✅ Step 2: แลก code + shop_id เป็น access_token
    """
    path = "/api/v2/auth/token/get"
    timestamp = int(time.time())
    base_string = f"{PARTNER_ID}{path}{timestamp}"

    sign = hmac.new(PARTNER_KEY.encode(), base_string.encode(), hashlib.sha256).hexdigest()

    url = (
        f"{AUTH_BASE_URL}{path}"
        f"?partner_id={PARTNER_ID}"
        f"&timestamp={timestamp}"
        f"&sign={sign}"
    )

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
