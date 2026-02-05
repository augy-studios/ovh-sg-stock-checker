import os
import requests
from datetime import datetime, timezone
from zoneinfo import ZoneInfo 

from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

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

    datacenters = data.get("datacenters", [])

    sg_linux_status = None
    for dc in datacenters:
        if dc.get("datacenter") == "SGP":
            sg_linux_status = dc.get("linuxStatus")
            break

    now_sgt = datetime.now(timezone.utc).astimezone(ZoneInfo("Asia/Singapore"))
    timestamp = now_sgt.strftime("%Y-%m-%d %H:%M:%S SGT")

    if sg_linux_status == "available":
        status_icon = "✅"
        status_text = "Available"
    elif sg_linux_status == "out-of-stock":
        status_icon = "❌"
        status_text = "Out of stock"
    else:
        status_icon = "⚠️"
        status_text = f"Unknown ({sg_linux_status})"

    message = (
        "🔔 <b>OVHCloud VPS Status Check - Singapore</b>\n\n"
        "📍 <b>Datacenter:</b> Singapore (SGP)\n"
        f"🕐 <b>Time:</b> {timestamp}\n\n"
        "🐧 <b>Linux VPS Status:</b>\n"
        f"{status_icon} {status_text}\n\n"
        "Order page:\n"
        "https://www.ovhcloud.com/en-sg/vps/"
    )

if __name__ == "__main__":
    check_stock()
