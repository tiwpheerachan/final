from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import os
import time
import hmac
import hashlib
import requests
import traceback
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client

# ✅ โหลด ENV
load_dotenv()

# ✅ FastAPI app
app = FastAPI()
templates = Jinja2Templates(directory="templates")

# ✅ Shopee API Config
PARTNER_ID = int(os.getenv("PARTNER_ID"))
PARTNER_KEY = os.getenv("PARTNER_KEY")
REDIRECT_URL = os.getenv("REDIRECT_URL")
BASE_URL = "https://partner.shopeemobile.com"

# ✅ Supabase SDK Init
SUPABASE_URL = f"https://{os.getenv('DB_HOST')}"  # ใช้ HOST จาก env
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

# ✅ ฟังก์ชันสำหรับแปลง timestamp ใน template
def format_datetime_filter(value):
    try:
        return datetime.fromtimestamp(value).strftime('%Y-%m-%d %H:%M:%S')
    except:
        return value
templates.env.filters['datetime'] = format_datetime_filter

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

        response_json = response.json()
        if response_json.get("error"):
            return JSONResponse(status_code=400, content={
                "error": "API returned error",
                "details": response_json
            })

        data = response_json["data"]
        access_token = data.get("access_token")
        refresh_token = data.get("refresh_token")
        expire_in = data.get("expire_in")

        if not access_token:
            return JSONResponse(status_code=400, content={"error": "Missing access_token in API response"})

        token_data = {
            "shop_id": int(shop_id),
            "access_token": str(access_token),
            "refresh_token": str(refresh_token) if refresh_token else None,
            "expire_in": int(expire_in) if expire_in else None,
            "last_updated": datetime.utcnow().isoformat()
        }

        supabase.table("shopee_tokens").upsert(token_data).execute()

        return {
            "message": "✅ Access Token Retrieved and Saved!",
            "shop_id": shop_id,
            "token_saved": True
        }

    except Exception as e:
        traceback.print_exc()
        return JSONResponse(status_code=500, content={
            "error": "Unexpected error in /callback",
            "details": str(e)
        })

# ✅ ดึงคำสั่งซื้อ (API JSON)
@app.get("/orders")
def get_orders():
    from shopee_fetcher import get_order_list
    return get_order_list(
        access_token=os.getenv("ACCESS_TOKEN"),
        shop_id=os.getenv("SHOP_ID"),
        time_gap_seconds=86400
    )

# ✅ แสดงผลคำสั่งซื้อบนเว็บ (Jinja2 UI)
@app.get("/orders/view", response_class=HTMLResponse)
async def view_orders(request: Request):
    try:
        from shopee_fetcher import get_order_list
        response = get_order_list(
            access_token=os.getenv("ACCESS_TOKEN"),
            shop_id=os.getenv("SHOP_ID"),
            time_gap_seconds=86400
        )
        orders = response.get("order_list", [])
        return templates.TemplateResponse("orders.html", {
            "request": request,
            "orders": orders
        })
    except Exception as e:
        traceback.print_exc()
        return templates.TemplateResponse("orders.html", {
            "request": request,
            "orders": [],
            "error": str(e)
        })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
