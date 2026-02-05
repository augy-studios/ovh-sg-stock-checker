import os
import requests
from datetime import datetime

API_URL = "https://www.ovhcloud.com/ca/engine/api/v1/vps/order/rule/datacenter/?ovhSubsidiary=SG&os=Debian%2013&planCode=vps-2025-model2"

# VPS models to check
VPS_MODELS = [
    "VPS-1",
    "VPS-2",
    "VPS-3",
    "VPS-4",
    "VPS-5",
    "VPS-6",
]

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_IDS = os.getenv("TELEGRAM_CHAT_IDS", "")  # comma separated


def send_telegram(message: str):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_IDS:
        print("Telegram not configured.")
        return

    for chat_id in TELEGRAM_CHAT_IDS.split(","):
        chat_id = chat_id.strip()
        if not chat_id:
            continue

        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "HTML",
        }

        try:
            requests.post(url, json=payload, timeout=15)
        except Exception as e:
            print(f"Failed to send Telegram message to {chat_id}: {e}")


def check_stock():
    try:
        response = requests.get(API_URL, timeout=30)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        msg = f"❌ OVH API request failed: {e}"
        print(msg)
        send_telegram(msg)
        return

    available = []
    out_of_stock = []

    # Expected structure: list of plans with availability status
    for item in data:
        plan = item.get("planCode", "")
        availability = item.get("availability", "")

        for model in VPS_MODELS:
            if model.lower() in plan.lower():
                if availability.lower() == "available":
                    available.append(model)
                else:
                    out_of_stock.append(model)

    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    message_lines = [
        f"<b>OVH SG VPS Stock Check</b>",
        f"Time: {timestamp}",
        "",
        "<b>Available:</b>",
    ]

    if available:
        message_lines.extend([f"✅ {m}" for m in sorted(set(available))])
    else:
        message_lines.append("(none)")

    message_lines.append("")
    message_lines.append("<b>Out of Stock:</b>")

    if out_of_stock:
        message_lines.extend([f"❌ {m}" for m in sorted(set(out_of_stock))])
    else:
        message_lines.append("(none)")

    message = "\n".join(message_lines)

    print(message)

    if available:
        send_telegram(message)


if __name__ == "__main__":
    check_stock()