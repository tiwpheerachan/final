from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import os
import time
import hmac
import hashlib
import requests
from dotenv import load_dotenv

load_dotenv(".env.production")

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# โหลดค่าจาก .env.production
PARTNER_ID = int(os.getenv("PARTNER_ID"))
PARTNER_KEY = os.getenv("PARTNER_KEY")
REDIRECT_URL = os.getenv("REDIRECT_URL")

# 🌐 Shopee Production API
BASE_URL = "https://partner.shopeemobile.com"

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

    return {
        "message": "✅ Access Token Retrieved!",
        "data": response.json()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main_production:app", host="0.0.0.0", port=10000)
