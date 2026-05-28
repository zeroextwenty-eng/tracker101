import asyncio
import websockets
import json
import aiohttp
import os
from flask import Flask
from threading import Thread

app = Flask('')
@app.route('/')
def home():
    return "Nerium Tracker Online"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

WS_URL = "wss://neriumsearch.onrender.com/"
FREE_WEBHOOK = os.getenv('FREE_WEBHOOK')
PAID_WEBHOOK = os.getenv('PAID_WEBHOOK')
FREE_ROLE = os.getenv('FREE_ROLE')
PAID_ROLE = os.getenv('PAID_ROLE')

async def send_webhook(url, role_id, item):
    async with aiohttp.ClientSession() as session:
        name = item.get('name') or item.get('item_name') or "Unknown Item"
        link = item.get('link') or item.get('item_link') or "https://www.roblox.com/catalog"
        price = str(item.get('price') or item.get('item_price') or "0")
        image = item.get('image') or item.get('thumbnail') or ""

        is_free = price == "0" or "free" in price.lower()
        color = 65280 if is_free else 16711680

        payload = {
            "content": f"<@&{role_id}>",
            "embeds": [{
                "title": name,
                "url": link,
                "color": color,
                "fields": [
                    {"name": "Price", "value": f"💵 {price}", "inline": True},
                    {"name": "Link", "value": f"[Click to Open]({link})", "inline": True}
                ],
                "thumbnail": {"url": image},
                "footer": {"text": "Nerium Search Real-Time"}
            }]
        }
        try:
            async with session.post(url, json=payload) as resp:
                return resp.status
        except Exception:
            return None

async def monitor():
    while True:
        try:
            async with websockets.connect(WS_URL) as ws:
                print("WebSocket Connected")
                while True:
                    data = await ws.recv()
                    item = json.loads(data)
                    
                    price_val = str(item.get('price', '0')).lower()
                    
                    if price_val == "0" or "free" in price_val:
                        await send_webhook(FREE_WEBHOOK, FREE_ROLE, item)
                    else:
                        await send_webhook(PAID_WEBHOOK, PAID_ROLE, item)
        except Exception as e:
            print(f"Connection lost, retrying: {e}")
            await asyncio.sleep(5)

if __name__ == "__main__":
    Thread(target=run_flask).start()
    asyncio.run(monitor())
