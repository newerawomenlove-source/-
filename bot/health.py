import asyncio
import logging
import time

from aiogram import Bot
from aiohttp import web

logger = logging.getLogger(__name__)

HEALTH_PORT = 8080
HEARTBEAT_INTERVAL_SECONDS = 60
STALE_AFTER_SECONDS = 180

_last_success = time.monotonic()


async def _heartbeat_loop(bot: Bot) -> None:
    global _last_success
    while True:
        try:
            await bot.get_me()
            _last_success = time.monotonic()
        except Exception:
            logger.warning("Heartbeat check failed (bot can't reach Telegram right now)")
        await asyncio.sleep(HEARTBEAT_INTERVAL_SECONDS)


async def _health_handler(request: web.Request) -> web.Response:
    age = time.monotonic() - _last_success
    if age < STALE_AFTER_SECONDS:
        return web.Response(text="OK", status=200)
    return web.Response(text=f"STALE: {int(age)}s since last successful Telegram check", status=503)


async def run_health_server(bot: Bot) -> None:
    asyncio.create_task(_heartbeat_loop(bot))
    app = web.Application()
    app.router.add_get("/health", _health_handler)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", HEALTH_PORT)
    await site.start()
    logger.info("Health check server listening on :%s/health", HEALTH_PORT)
