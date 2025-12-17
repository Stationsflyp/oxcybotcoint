import requests
import json

WEBHOOK_URL = "https://discord.com/api/webhooks/1450953186876719164/TqBa1UV_vhunY1jM3edZVquRG9qWCCNrlACbbIqajTvUI16QP9sHIV-5K8LkKcR3NMfu"

# Banner image
BANNER_URL = "https://i.ibb.co/qLKxjsS5/pngwing-com.png"

EMBED = {
    "username": "OxcyShop - Points Store",
    "avatar_url": BANNER_URL,
    "embeds": [
        {
            "title": "OxcyShop — Free Points Shop",
            "description": (
                "**🇬🇧 English:**\n"
                "This is a **free shop** where you can earn rewards for your activity in the server. "
                "In the [approval channel](https://discord.com/channels/1286045119715475527/1447279516861989046) "
                "you will find IMGUIs waiting for approval. **Not all of them are premium**, and receiving them is not guaranteed.\n\n"
                "In this point shop, you earn coins by participating: chatting, joining voice channels, and contributing to the community. "
                "You can also check the **[leaderboard](https://discord.com/channels/1286045119715475527/1450555229719498946)** to see your current coins.\n"
                "Once you reach enough points, you can redeem them for **more premium IMGUIs** in this channel: "
                "[Redeem IMGUIs](https://discord.com/channels/1286045119715475527/1450555415673962678)\n\n"
                "💡 **Note:** This shop is **100% free**, no real money is required to get points or IMGUIs.\n\n"

                "**🇪🇸 Español:**\n"
                "Esta es una **tienda gratuita** donde puedes obtener recompensas por tu actividad en el servidor. "
                "En el [canal de aprobación](https://discord.com/channels/1286045119715475527/1447279516861989046) "
                "encontrarás IMGUIs pendientes de aprobación. **No todas son premium**, y recibirlas **no está garantizado**.\n\n"
                "En esta tienda de puntos, ganarás monedas por participar: hablar, unirte a chats de voz y colaborar en la comunidad. "
                "También puedes revisar la **[tabla de posiciones](https://discord.com/channels/1286045119715475527/1450555229719498946)** para ver tus monedas actuales.\n"
                "Al acumular suficientes puntos, podrás canjearlos por **IMGUIs más premium** en este canal: "
                "[Canje de IMGUIs](https://discord.com/channels/1286045119715475527/1450555415673962678)\n\n"
                "💡 **Nota:** Esta tienda es **100% gratuita**, no se requiere dinero real para obtener puntos o IMGUIs."
            ),
            "color": 0xFF8C00,  # Dark orange
            "image": {"url": BANNER_URL},
            "footer": {"text": "OxcyShop - Free Points Shop | Earn rewards by activity"}
        }
    ]
}

headers = {"Content-Type": "application/json"}
response = requests.post(WEBHOOK_URL, data=json.dumps(EMBED), headers=headers)

if response.status_code == 204:
    print("✅ Embed sent successfully!")
else:
    print(f"❌ Failed to send embed. Status code: {response.status_code}, Response: {response.text}")
