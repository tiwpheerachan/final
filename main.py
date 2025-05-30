from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
import os
import uvicorn

app = FastAPI()

@app.get("/")
async def root(request: Request):
    code = request.query_params.get("code")
    shop_id = request.query_params.get("shop_id")

    # Shopee จะ redirect กลับมาที่ / พร้อม query string
    if code and shop_id:
        return RedirectResponse(url=f"/callback?code={code}&shop_id={shop_id}")
    return {"message": "Shopee API Redirect Handler Root"}

@app.get("/callback")
async def callback(request: Request):
    code = request.query_params.get("code")
    shop_id = request.query_params.get("shop_id")

    if not code or not shop_id:
        return {"error": "Missing code or shop_id"}
    
    # ในขั้นตอนต่อไปจะใช้ code และ shop_id ไปขอ access_token
    return {
        "message": "Shopee Auth Code Received!",
        "code": code,
        "shop_id": shop_id
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=10000)
