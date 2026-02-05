import os
import requests
from dotenv import load_dotenv

load_dotenv(".env")

token = os.getenv("TELEGRAM_BOT_TOKEN")
chat_ids = os.getenv("TELEGRAM_CHAT_IDS", "").split(",")

for chat in chat_ids:
    chat = chat.strip()
    if not chat:
        continue

    r = requests.post(
        f"https://api.telegram.org/bot{token}/sendMessage",
        json={"chat_id": chat, "text": "✅ Telegram test successful"}
    )
    print(chat, r.text)
