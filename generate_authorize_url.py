# 📁 generate_authorize_url.py
import time
import hmac
import hashlib
import os
from dotenv import load_dotenv

# ✅ โหลดค่าจาก .env หรือกำหนดตรงนี้
load_dotenv()

# กำหนดค่าจาก Shopee Console ของคุณ
partner_id = os.getenv("PARTNER_ID") or "2011520"
partner_key = os.getenv("PARTNER_KEY") or "707378444d6c6652564a4276584969477f6617a4f6a75487069547745746e6b4b"
redirect = os.getenv("REDIRECT_URL") or "https://final-e74d.onrender.com/callback"
path = "/api/v2/shop/auth_partner"

# ✅ สร้าง timestamp และ sign
timestamp = int(time.time())
base_string = f"{partner_id}{path}{timestamp}"
sign = hmac.new(partner_key.encode(), base_string.encode(), hashlib.sha256).hexdigest()

# ✅ สร้าง URL ที่ร้านค้าจะเข้าไป authorize
auth_url = (
    f"https://partner.shopeemobile.com{path}"
    f"?partner_id={partner_id}"
    f"&timestamp={timestamp}"
    f"&sign={sign}"
    f"&redirect={redirect}"
)

# ✅ แสดงผลลิงก์
print("🔗 Authorize this shop by visiting:\n")
print(auth_url)
