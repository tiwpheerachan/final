from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
import os
import time
import hmac
import hashlib
import httpx

app = FastAPI()

# ENV variables
PARTNER_ID = int(os.getenv("PARTNER_ID"))
PARTNER_KEY = os.getenv("PARTNER_KEY")
REDIRECT_URL = os.getenv("REDIRECT_URL")

templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    code = request.query_params.get("code")
    shop_id = request.query_params.get("shop_id")

    if code and shop_id:
        return RedirectResponse(url=f"/callback?code={code}&shop_id={shop_id}")
    
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/callback")
async def callback(request: Request):
    code = request.query_params.get("code")
    shop_id = request.query_params.get("shop_id")

    if not code or not shop_id:
        return JSONResponse(status_code=400, content={"error": "Missing code or shop_id"})

    # Prepare request to get access token
    timestamp = int(time.time())
    path = "/api/v2/auth/token/get"

    base_string = f"{PARTNER_ID}{path}{timestamp}{PARTNER_ID}{shop_id}{code}"
    sign = hmac.new(PARTNER_KEY.encode('utf-8'), base_string.encode('utf-8'), hashlib.sha256).hexdigest()

    url = f"https://partner.shopeemobile.com{path}"
    payload = {
        "code": code,
        "partner_id": PARTNER_ID,
        "shop_id": int(shop_id),
        "sign": sign,
        "timestamp": timestamp
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload)
    
    if response.status_code != 200:
        return JSONResponse(status_code=response.status_code, content={"error": "Failed to get token", "details": response.text})

    data = response.json()

    return {
        "message": "Access Token Retrieved!",
        "data": data
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=10000)
