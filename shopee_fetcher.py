import hashlib
import hmac
import time
import requests
import json

def get_order_list(partner_id, partner_key, access_token, shop_id):
    path = "/api/v2/order/get_order_list"
    base_url = "https://partner.shopeemobile.com"
    timestamp = int(time.time())
    sign = make_signature(partner_id, path, timestamp, access_token, shop_id, partner_key)
    url = f"{base_url}{path}?partner_id={partner_id}&timestamp={timestamp}&access_token={access_token}&shop_id={shop_id}&sign={sign}&time_range_field=create_time&time_from={timestamp-3600}&time_to={timestamp}"

    response = requests.get(url)
    return response.json()

def make_signature(partner_id, path, timestamp, access_token, shop_id, partner_key):
    base_string = f"{partner_id}{path}{timestamp}{access_token}{shop_id}"
    return hmac.new(
        bytes(partner_key, 'utf-8'),
        base_string.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
