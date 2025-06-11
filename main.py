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

        print(f"✅ Received callback with code: {code} and shop_id: {shop_id}")

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

        print(f"✅ Sending request to Shopee API: {url}")
        print(f"✅ Payload: {payload}")

        response = requests.post(url, json=payload)
        
        print(f"✅ Shopee API response status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ API Error: {response.text}")
            return JSONResponse(status_code=response.status_code, content={
                "error": "Failed to get token",
                "details": response.text
            })

        # แสดงข้อมูลทั้งหมดที่ได้รับจาก API เพื่อ debug
        response_json = response.json()
        print(f"✅ Full API Response: {response_json}")
        
        # ตรวจสอบโครงสร้างของ response
        if "error" in response_json:
            print(f"❌ API returned error: {response_json['error']}")
            return JSONResponse(status_code=400, content={
                "error": "API returned error",
                "details": response_json
            })
            
        data = response_json.get("data", {})
        
        # ตรวจสอบว่ามีข้อมูล token หรือไม่
        if not data:
            print("❌ No data in API response")
            return JSONResponse(status_code=400, content={
                "error": "No data in API response",
                "response": response_json
            })
            
        # ตรวจสอบค่า token ที่ได้รับ
        access_token = data.get("access_token")
        refresh_token = data.get("refresh_token")
        expire_in = data.get("expire_in")
        
        print(f"✅ Access Token: {access_token[:10]}... (truncated)")
        print(f"✅ Refresh Token: {refresh_token[:10]}... (truncated)" if refresh_token else "❌ No refresh_token")
        print(f"✅ Expire In: {expire_in}" if expire_in else "❌ No expire_in")
        
        if not access_token:
            print("❌ Missing access_token in API response")
            return JSONResponse(status_code=400, content={
                "error": "Missing access_token in API response",
                "data": data
            })

        # สร้างข้อมูลที่จะบันทึกลง Supabase
        token_data = {
            "shop_id": int(shop_id),
            "access_token": str(access_token),
            "refresh_token": str(refresh_token) if refresh_token else None,
            "expire_in": int(expire_in) if expire_in else None,
            "last_updated": datetime.utcnow().isoformat()
        }
        
        print(f"✅ Data to be saved to Supabase: {token_data}")

        # ✅ บันทึกลง Supabase
        try:
            result = supabase.table("shopee_tokens").upsert(token_data).execute()
            print(f"✅ Supabase response: {result}")
            print(f"✅ Token saved to Supabase for shop_id {shop_id}")

        except Exception as db_err:
            print(f"❌ Supabase write error: {db_err}")
            traceback.print_exc()  # แสดง stack trace เพื่อ debug
            return JSONResponse(status_code=500, content={
                "error": "Supabase write error",
                "details": str(db_err)
            })

        return {
            "message": "✅ Access Token Retrieved and Saved!",
            "shop_id": shop_id,
            "token_saved": True
        }

    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        traceback.print_exc()  # แสดง stack trace เพื่อ debug
        return JSONResponse(status_code=500, content={
            "error": "Unexpected error in /callback",
            "details": str(e)
        })


# ✅ รัน Local
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=10000)