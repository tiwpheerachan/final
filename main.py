# main.py
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
import time, hmac, hashlib
import os

app = FastAPI()

@app.get("/")
async def root(request: Request):
    code = request.query_params.get("code")
    shop_id = request.query_params.get("shop_id")
    if code and shop_id:
        return RedirectResponse(url=f"/callback?code={code}&shop_id={shop_id}")
    return {"message": "Shopee API Redirect Handler Root"}

@app.get("/callback")
async def callback(request: Request):
    code = request.query_params.get("code")
    shop_id = request.query_params.get("shop_id")
    if not code or not shop_id:
        return {"error": "Missing code or shop_id"}
    return {
        "message": "Shopee Auth Code Received!",
        "code": code,
        "shop_id": shop_id
    }

@app.get("/login")
async def login():
    partner_id = os.getenv("PARTNER_ID")
    partner_key = os.getenv("PARTNER_KEY")
    redirect_url = os.getenv("REDIRECT_URL")
    
    print("partner_id:", partner_id)
    print("partner_key:", partner_key)
    print("redirect_url:", redirect_url)

    if not partner_id or not partner_key or not redirect_url:
        return {"error": "Missing env variables"}

    path = "/api/v2/shop/auth_partner"
    timestamp = int(time.time())
    base_string = f"{partner_id}{path}{timestamp}"
    sign = hmac.new(partner_key.encode(), base_string.encode(), hashlib.sha256).hexdigest()

    auth_url = f"https://partner.shopeemobile.com{path}?partner_id={partner_id}&timestamp={timestamp}&sign={sign}&redirect={redirect_url}"
    
    return RedirectResponse(url=auth_url)
