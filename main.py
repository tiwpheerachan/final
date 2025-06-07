from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
import os
import time
import hmac
import hashlib
import requests

app = FastAPI()

# ✅ ข้อมูลจาก Shopee Console
PARTNER_ID = int(os.getenv("PARTNER_ID", "1280109"))
PARTNER_KEY = os.getenv("PARTNER_KEY", "5a4e6e4c4d4375464c57506b7a42775a77466d686c534255574267514f494a54")
REDIRECT_URL = os.getenv("REDIRECT_URL", "https://final-e74d.onrender.com/callback")

templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    timestamp = int(time.time())
    base_string = f"{PARTNER_ID}/api/v2/shop/auth_partner{timestamp}"
    sign = hmac.new(PARTNER_KEY.encode(), base_string.encode(), hashlib.sha256).hexdigest()

    login_url = (
        f"https://partner.test-stable.shopeemobile.com/api/v2/shop/auth_partner"
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

    # 🔐 Get access token
    timestamp = int(time.time())
    path = "/api/v2/auth/token/get"
    base_string = f"{PARTNER_ID}{path}{timestamp}"
    sign = hmac.new(PARTNER_KEY.encode(), base_string.encode(), hashlib.sha256).hexdigest()

    url = (
        f"https://partner.test-stable.shopeemobile.com{path}"
        f"?partner_id={PARTNER_ID}"
        f"&timestamp={timestamp}"
        f"&sign={sign}"
    )

    payload = {
        "code": code,
        "partner_id": PARTNER_ID,
        "shop_id": int(shop_id),
    }

    headers = {"Content-Type": "application/json"}

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code != 200:
        return JSONResponse(status_code=response.status_code, content={
            "error": "Failed to get token",
            "details": response.text
        })

    return {
        "message": "Access Token Retrieved!",
        "data": response.json()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=10000)
