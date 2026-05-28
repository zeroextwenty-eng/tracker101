async def send_webhook(session, url, role_id, item):
    if not url:
        return

    try:
        name = (
            item.get("name")
            or item.get("itemName")
            or item.get("item_name")
            or item.get("title")
            or "Unknown Item"
        )

        link = (
            item.get("link")
            or item.get("itemLink")
            or item.get("item_link")
            or item.get("url")
            or "https://www.roblox.com/catalog"
        )

        image = (
            item.get("image")
            or item.get("thumbnail")
            or item.get("item_image")
            or item.get("item_thumbnail")
        )

        try:
            price_num = int(float(item.get("price", 0)))
        except:
            price_num = 0

        is_free = price_num == 0
        color = 0x00FF00 if is_free else 0xFF0000

        role_ping = f"<@&{role_id}>" if role_id and str(role_id).lower() != "none" else "@here"

        # Better embed based on your screenshot
        embed = {
            "title": "Collectible Found" if is_free else name,
            "url": link,
            "color": color,
            "fields": [
                {
                    "name": "Price",
                    "value": f"💰 {price_num} Robux",
                    "inline": True
                },
                {
                    "name": "Status",
                    "value": "✅ FREE" if is_free else "PAID",
                    "inline": True
                }
            ],
            "footer": {
                "text": "Nerium Search Real-Time"
            }
        }

        if name == "Unknown Item" and is_free:
            embed["title"] = "Unknown Item"
            embed["fields"][1]["name"] = "Link"
            embed["fields"][1]["value"] = f"[Click to Open]({link})"

        if image:
            embed["thumbnail"] = {"url": image}

        payload = {
            "content": role_ping,
            "embeds": [embed]
        }

        async with session.post(url, json=payload, timeout=10) as response:
            if response.status not in (200, 204):
                print(f"Webhook failed: {response.status}")

    except Exception as e:
        print(f"Webhook error: {e}")
