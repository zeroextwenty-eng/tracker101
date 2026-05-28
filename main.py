import asyncio
import websockets
import json
import aiohttp
import os
import logging

WS_URL = "wss://neriumsearch.onrender.com/"

FREE_WEBHOOK = os.getenv("FREE_WEBHOOK")
PAID_WEBHOOK = os.getenv("PAID_WEBHOOK")

FREE_ROLE = os.getenv("FREE_ROLE")
PAID_ROLE = os.getenv("PAID_ROLE")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

async def send_webhook(session, url, role_id, item):
    if not url:
        logging.warning("Webhook URL missing.")
        return

    try:
        name = (
            item.get("name")
            or item.get("itemName")
            or item.get("item_name")
            or "Collectible Found"
        )

        link = (
            item.get("link")
            or item.get("itemLink")
            or item.get("item_link")
            or "https://www.roblox.com/catalog"
        )

        image = (
            item.get("image")
            or item.get("thumbnail")
            or item.get("item_image")
            or item.get("item_thumbnail")
            or ""
        )

        raw_price = item.get("price", 0)
        price = str(raw_price)

        is_free = (
            str(raw_price).lower() == "0"
            or "free" in str(raw_price).lower()
        )

        color = 65280 if is_free else 16711680

        role_ping = (
            f"<@&{role_id}>"
            if role_id and role_id.lower() != "none"
            else "@here"
        )

        payload = {
            "content": role_ping,
            "embeds": [
                {
                    "title": name,
                    "url": link,
                    "color": color,
                    "fields": [
                        {
                            "name": "Price",
                            "value": f"💵 {price}",
                            "inline": True
                        },
                        {
                            "name": "Status",
                            "value": "FREE" if is_free else "PAID",
                            "inline": True
                        }
                    ],
                    "footer": {
                        "text": "Nerium Search Monitor"
                    }
                }
            ]
        }

        if image:
            payload["embeds"][0]["image"] = {"url": image}

        async with session.post(url, json=payload) as response:
            if response.status not in [200, 204]:
                text = await response.text()
                logging.error(
                    f"Webhook failed ({response.status}): {text}"
                )
            else:
                logging.info(f"Webhook sent: {name}")

    except Exception as e:
        logging.error(f"Webhook error: {e}")

async def monitor():
    while True:
        try:
            logging.info("Connecting to websocket...")

            async with aiohttp.ClientSession() as session:
                async with websockets.connect(
                    WS_URL,
                    ping_interval=20,
                    ping_timeout=20
                ) as ws:

                    logging.info("Connected.")

                    async for data in ws:
                        try:
                            item = json.loads(data)

                            raw_price = str(
                                item.get("price", "0")
                            ).lower()

                            is_free = (
                                raw_price == "0"
                                or "free" in raw_price
                            )

                            if is_free:
                                await send_webhook(
                                    session,
                                    FREE_WEBHOOK,
                                    FREE_ROLE,
                                    item
                                )
                            else:
                                await send_webhook(
                                    session,
                                    PAID_WEBHOOK,
                                    PAID_ROLE,
                                    item
                                )

                        except json.JSONDecodeError:
                            logging.warning("Invalid JSON received.")

                        except Exception as e:
                            logging.error(f"Processing error: {e}")

        except websockets.exceptions.ConnectionClosed:
            logging.warning("Websocket disconnected.")

        except Exception as e:
            logging.error(f"Connection error: {e}")

        logging.info("Reconnecting in 5 seconds...")
        await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(monitor())
