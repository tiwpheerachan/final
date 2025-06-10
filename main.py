from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import os
import time
import hmac
import hashlib
import requests
import psycopg2
from dotenv import load_dotenv
from datetime import datetime

# โหลด .env
load_dotenv(".env.production")

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# โหลดค่าจาก ENV
PARTNER_ID = int(os.getenv("PARTNER_ID"))
PARTNER_KEY = os.getenv("PARTNER_KEY")
REDIRECT_URL = os.getenv("REDIRECT_URL")
BASE_URL = "https://partner.shopeemobile.com"

# 🧠 Database Connection (Supabase / PostgreSQL)
DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
}

@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    timestamp = int(time.time())
    path = "/api/v2/shop/auth_partner"
    base_string = f"{PARTNER_ID}{path}{timestamp}"
    sign = hmac.new(PARTNER_KEY.encode(), base_string.encode(), hashlib.sha256).hexdigest()

    login_url = (
        f"{BASE_URL}{path}"
        f"?partner_id={PARTNER_ID}"
        f"&timestamp={timestamp}"
        f"&sign={sign}"
        f"&redirect={REDIRECT_URL}"
    )

    return templates.TemplateResponse("login.html", {
        "request": request,
        "login_url": login_url
    })

@app.get("/callback")
async def callback(request: Request):
    code = request.query_params.get("code")
    shop_id = request.query_params.get("shop_id")

    if not code or not shop_id:
        return JSONResponse(status_code=400, content={"error": "Missing code or shop_id"})

    timestamp = int(time.time())
    path = "/api/v2/auth/token/get"
    base_string = f"{PARTNER_ID}{path}{timestamp}"
    sign = hmac.new(PARTNER_KEY.encode(), base_string.encode(), hashlib.sha256).hexdigest()

    url = (
        f"{BASE_URL}{path}"
        f"?partner_id={PARTNER_ID}"
        f"&timestamp={timestamp}"
        f"&sign={sign}"
    )

    payload = {
        "code": code,
        "partner_id": PARTNER_ID,
        "shop_id": int(shop_id),
    }

    response = requests.post(url, json=payload)

    if response.status_code != 200:
        return JSONResponse(status_code=response.status_code, content={
            "error": "Failed to get token",
            "details": response.text
        })

    data = response.json().get("data", {})

    # ✅ บันทึก Token ลง DB
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS shopee_tokens (
                shop_id BIGINT PRIMARY KEY,
                access_token TEXT,
                refresh_token TEXT,
                expire_in INTEGER,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            INSERT INTO shopee_tokens (shop_id, access_token, refresh_token, expire_in, last_updated)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (shop_id) DO UPDATE
            SET access_token = EXCLUDED.access_token,
                refresh_token = EXCLUDED.refresh_token,
                expire_in = EXCLUDED.expire_in,
                last_updated = CURRENT_TIMESTAMP
        """, (
            shop_id,
            data.get("access_token"),
            data.get("refresh_token"),
            data.get("expire_in"),
            datetime.utcnow()
        ))

        conn.commit()
        cursor.close()
        conn.close()
        print(f"✅ Token saved for shop_id {shop_id}")

    except Exception as db_err:
        return JSONResponse(status_code=500, content={"error": "DB write error", "details": str(db_err)})

    return {
        "message": "✅ Access Token Retrieved!",
        "data": data
    }

# 🟢 LOCAL ONLY: ใช้ตอนรัน dev
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=10000)
