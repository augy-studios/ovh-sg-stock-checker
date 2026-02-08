import os
import requests
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from dotenv import load_dotenv

# Load .env safely
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

# VPS-2 (model2)
API_VPS2 = "https://www.ovhcloud.com/ca/engine/api/v1/vps/order/rule/datacenter/?ovhSubsidiary=SG&os=Debian%2013&planCode=vps-2025-model2"

# VPS-1 (model1)
API_VPS1 = "https://www.ovhcloud.com/ca/engine/api/v1/vps/order/rule/datacenter/?ovhSubsidiary=SG&os=Debian%2013&planCode=vps-2025-model1"

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_IDS = os.getenv("TELEGRAM_CHAT_IDS", "")


def send_telegram(message: str):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_IDS:
        print("❌ Telegram not configured.")
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
            r = requests.post(url, json=payload, timeout=15)
            print(f"Telegram response ({chat_id}): {r.text}")
        except Exception as e:
            print(f"Failed to send Telegram message to {chat_id}: {e}")


def get_sg_linux_status(api_url):
    try:
        r = requests.get(api_url, timeout=30)
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        print(f"API error ({api_url}): {e}")
        return None

    for dc in data.get("datacenters", []):
        if dc.get("datacenter") == "SGP":
            return dc.get("linuxStatus")
    return None


def check_stock():
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Checking OVH SG VPS-1 & VPS-2 Linux stock...")

    vps1_status = get_sg_linux_status(API_VPS1)
    vps2_status = get_sg_linux_status(API_VPS2)

    now_sgt = datetime.now(timezone.utc).astimezone(ZoneInfo("Asia/Singapore"))
    timestamp = now_sgt.strftime("%Y-%m-%d %H:%M:%S SGT")

    def icon(status):
        return "✅" if status == "available" else "❌"

    vps1_icon = icon(vps1_status)
    vps2_icon = icon(vps2_status)

    any_available = (vps1_status == "available") or (vps2_status == "available")

    message = (
        "🔔 <b>OVHCloud VPS Status Check - Singapore</b>\n\n"
        "📍 <b>Datacenter:</b> Singapore (SGP)\n"
        f"🕐 <b>Time:</b> {timestamp}\n\n"
        "🐧 <b>Linux VPS Availability:</b>\n"
        f"{vps1_icon} VPS-1\n"
        f"{vps2_icon} VPS-2\n"
    )

    if any_available:
        message += (
            "\nOrder page:\n"
            "https://www.ovhcloud.com/en-sg/vps/"
        )

    print(message)
    send_telegram(message)


if __name__ == "__main__":
    check_stock()
