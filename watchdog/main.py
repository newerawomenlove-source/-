import os
import time

import httpx

BOT_TOKEN = os.environ["BOT_TOKEN"]
HEALTH_URL = os.environ.get("HEALTH_URL", "http://135.106.182.116:8080/health")
ADMIN_CHAT_IDS = [chat_id.strip() for chat_id in os.environ.get("ADMIN_CHAT_ID", "").split(",") if chat_id.strip()]
CHECK_INTERVAL_SECONDS = int(os.environ.get("CHECK_INTERVAL_SECONDS", "180"))

DOWN_TEXT = "⚠️ Бот «Женщины нового времени» не отвечает уже несколько минут. Проверьте сервер (Selectel) и прокси."
RECOVERED_TEXT = "✅ Бот «Женщины нового времени» снова работает."


def notify(text: str) -> None:
    for chat_id in ADMIN_CHAT_IDS:
        try:
            httpx.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                data={"chat_id": chat_id, "text": text},
                timeout=15,
            )
        except Exception as exc:
            print(f"Failed to notify {chat_id}: {exc}")


def is_healthy() -> bool:
    try:
        response = httpx.get(HEALTH_URL, timeout=15)
        return response.status_code == 200
    except Exception:
        return False


def main() -> None:
    print(f"Watchdog started, checking {HEALTH_URL} every {CHECK_INTERVAL_SECONDS}s")
    was_healthy = True
    while True:
        healthy = is_healthy()
        if was_healthy and not healthy:
            print("ALERT: main bot appears down")
            notify(DOWN_TEXT)
        elif not was_healthy and healthy:
            print("Main bot recovered")
            notify(RECOVERED_TEXT)
        was_healthy = healthy
        time.sleep(CHECK_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
