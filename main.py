import asyncio
import websockets
import json
import aiohttp
import os

WS_URL = "wss://neriumsearch.onrender.com/"
FREE_WEBHOOK = os.getenv('FREE_WEBHOOK')
PAID_WEBHOOK = os.getenv('PAID_WEBHOOK')
FREE_ROLE = os.getenv('FREE_ROLE')
PAID_ROLE = os.getenv('PAID_ROLE')

async def send_webhook(url, role_id, item):
    async with aiohttp.ClientSession() as session:
        # Improved data detection
        name = item.get('name') or item.get('itemName') or item.get('item_name') or "Collectible Found"
        link = item.get('link') or item.get('itemLink') or item.get('item_link') or "https://www.roblox.com/catalog"
        price = str(item.get('price') if item.get('price') is not None else "0")
        image = item.get('image') or item.get('thumbnail') or item.get('item_image') or item.get('item_thumbnail') or ""

        is_free = price == "0" or "free" in price.lower()
        color = 65280 if is_free else 16711680
        
        # Fixing the @None issue
        role_ping = f"<@&{role_id}>" if role_id and role_id != "None" else "@here"

        payload = {
            "content": role_ping,
            "embeds": [{
                "title": name,
                "url": link,
                "color": color,
                "fields": [
                    {"name": "Price", "value": f"💵 {price}", "inline": True},
                    {"name": "Status", "value": "FREE" if is_free else "PAID", "inline": True}
                ],
                "image": {"url": image},  # Changed to 'image' for a large picture
                "footer": {"text": "Nerium Search Monitor"}
            }]
        }
        try:
            await session.post(url, json=payload)
        except:
            pass

async def monitor():
    while True:
        try:
            async with websockets.connect(WS_URL) as ws:
                while True:
                    data = await ws.recv()
                    item = json.loads(data)
                    price_val = str(item.get('price', '0')).lower()
                    
                    if price_val == "0" or "free" in price_val:
                        await send_webhook(FREE_WEBHOOK, FREE_ROLE, item)
                    else:
                        await send_webhook(PAID_WEBHOOK, PAID_ROLE, item)
        except:
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(monitor())
