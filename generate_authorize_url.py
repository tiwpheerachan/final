# 📁 generate_authorize_url.py
import time
import hmac
import hashlib
import os
from dotenv import load_dotenv

# ✅ โหลด .env
load_dotenv()

# ✅ ดึงค่าจาก .env
partner_id = os.getenv("PARTNER_ID")
partner_key = os.getenv("PARTNER_KEY")
redirect = os.getenv("REDIRECT_URL")
path = "/api/v2/shop/auth_partner"

# ✅ ตรวจสอบค่าที่จำเป็น
if not all([partner_id, partner_key, redirect]):
    raise ValueError("❌ โปรดตรวจสอบว่า PARTNER_ID, PARTNER_KEY และ REDIRECT_URL ถูกตั้งค่าไว้ใน .env")

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
