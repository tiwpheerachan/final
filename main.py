# main.py
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse

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
