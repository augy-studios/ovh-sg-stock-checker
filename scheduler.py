import time
import sqlite3
from datetime import datetime, timedelta, timezone
from checker import check_stock

DB_FILE = "scheduler.db"


def init_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS schedule (
            id INTEGER PRIMARY KEY,
            last_run TEXT
        )
    """)
    conn.commit()
    conn.close()


def get_last_run():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT last_run FROM schedule WHERE id = 1")
    row = cur.fetchone()
    conn.close()
    return datetime.fromisoformat(row[0]) if row else None


def set_last_run(ts: datetime):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO schedule (id, last_run)
        VALUES (1, ?)
        ON CONFLICT(id) DO UPDATE SET last_run=excluded.last_run
    """, (ts.isoformat(),))
    conn.commit()
    conn.close()


def next_run_30min(dt: datetime):
    base = dt.replace(second=0, microsecond=0)
    minute_block = (base.minute // 30) * 30
    next_block = base.replace(minute=minute_block) + timedelta(minutes=30)
    return next_block


def main():
    init_db()
    print("SQLite scheduler started (30-minute mode)...")

    while True:
        now = datetime.now(timezone.utc)
        last_run = get_last_run()

        if last_run is None:
            print("First run → executing check")
            check_stock()
            set_last_run(now)
        else:
            target = next_run_30min(last_run)
            if now >= target:
                print(f"30-minute trigger reached ({target}) → running check")
                check_stock()
                set_last_run(now)

        time.sleep(60)


if __name__ == "__main__":
    main()
