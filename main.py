from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import os
import time
import hmac
import hashlib
import requests
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client

# ✅ โหลด ENV
load_dotenv(".env.production")

# ✅ FastAPI app
app = FastAPI()
templates = Jinja2Templates(directory="templates")

# ✅ Shopee API Config
PARTNER_ID = int(os.getenv("PARTNER_ID"))
PARTNER_KEY = os.getenv("PARTNER_KEY")
REDIRECT_URL = os.getenv("REDIRECT_URL")
BASE_URL = "https://partner.shopeemobile.com"

# ✅ Supabase SDK Init
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

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
    try:
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

        # ✅ Insert to Supabase
        try:
            insert_response = supabase.table("shopee_tokens").upsert({
                "shop_id": int(shop_id),
                "access_token": data.get("access_token"),
                "refresh_token": data.get("refresh_token"),
                "expire_in": data.get("expire_in"),
                "last_updated": datetime.utcnow().isoformat()
            }).execute()

            print(f"✅ Token saved to Supabase for shop_id {shop_id}")

        except Exception as db_err:
            print("❌ Supabase DB Error:", db_err)
            return JSONResponse(status_code=500, content={
                "error": "Supabase write error",
                "details": str(db_err)
            })

        return {
            "message": "✅ Access Token Retrieved!",
            "data": data
        }

    except Exception as e:
        print("❌ เกิดข้อผิดพลาดใน /callback:", e)
        return JSONResponse(status_code=500, content={
            "error": "Unexpected error in /callback",
            "details": str(e)
        })

# ✅ Dev only: run with `python main.py`
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=10000)
