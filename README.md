# OVHCloud Singapore VPS Stock Checker

1. Clone repo
2. Install dependencies:
   pip3 install -r requirements.txt

3. Copy env file:
   cp .env.example .env

4. Edit `.env` with your Telegram bot token and chat IDs

5. Run manually:
   `python3 scheduler.py`

## Notes

- Script only sends Telegram notification when **any VPS becomes available**.
- Supports multiple Telegram recipients via comma-separated chat IDs.
- Designed for Debian/Linux servers.
