import time, os, hmac, hashlib, requests
import psycopg2
from dotenv import load_dotenv

load_dotenv()

# 📦 ENV
PARTNER_ID = os.getenv("PARTNER_ID")
PARTNER_KEY = os.getenv("PARTNER_KEY")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# 📂 Shopee API
BASE_URL = "https://partner.shopeemobile.com"
REFRESH_PATH = "/api/v2/auth/access_token/get"

def get_expiring_tokens():
    conn = psycopg2.connect(
        host=DB_HOST, port=DB_PORT, dbname=DB_NAME,
        user=DB_USER, password=DB_PASSWORD
    )
    cursor = conn.cursor()
    cursor.execute("""
        SELECT shop_id, refresh_token FROM shopee_tokens
        WHERE (EXTRACT(EPOCH FROM CURRENT_TIMESTAMP - last_updated) >= (expire_in - 600))
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows

def refresh_token(shop_id, refresh_token):
    timestamp = int(time.time())
    base_string = f"{PARTNER_ID}{REFRESH_PATH}{timestamp}"
    sign = hmac.new(PARTNER_KEY.encode(), base_string.encode(), hashlib.sha256).hexdigest()

    url = (
        f"{BASE_URL}{REFRESH_PATH}"
        f"?partner_id={PARTNER_ID}&timestamp={timestamp}&sign={sign}"
    )

    payload = {
        "refresh_token": refresh_token,
        "partner_id": int(PARTNER_ID),
        "shop_id": int(shop_id)
    }

    response = requests.post(url, json=payload)
    return response.json()

def update_token_in_db(shop_id, new_token, refresh_token, expire_in):
    conn = psycopg2.connect(
        host=DB_HOST, port=DB_PORT, dbname=DB_NAME,
        user=DB_USER, password=DB_PASSWORD
    )
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE shopee_tokens
        SET access_token = %s,
            refresh_token = %s,
            expire_in = %s,
            last_updated = CURRENT_TIMESTAMP
        WHERE shop_id = %s
    """, (new_token, refresh_token, expire_in, shop_id))
    conn.commit()
    conn.close()

def refresh_loop():
    print("🔁 Checking for tokens to refresh...")
    for shop_id, old_refresh in get_expiring_tokens():
        print(f"🔄 Refreshing token for shop_id: {shop_id}")
        result = refresh_token(shop_id, old_refresh)
        data = result.get("data", {})
        if data.get("access_token"):
            update_token_in_db(
                shop_id,
                data["access_token"],
                data["refresh_token"],
                data["expire_in"]
            )
            print(f"✅ Updated token for shop {shop_id}")
        else:
            print(f"❌ Failed for shop {shop_id}: {result.get('message')}")

if __name__ == "__main__":
    refresh_loop()
