import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from bot import db
from bot.config import BOT_TOKEN, PROXY_URL
from bot.handlers import funnel, moderation, screening, survey
from bot.health import run_health_server


async def main() -> None:
    logging.basicConfig(level=logging.INFO)

    await db.init_client()

    session = AiohttpSession(proxy=PROXY_URL) if PROXY_URL else None
    bot = Bot(token=BOT_TOKEN, session=session, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage())
    if moderation.MODERATION_ENABLED:
        dp.include_router(moderation.router)
    dp.include_router(survey.router)
    dp.include_router(funnel.router)
    if screening.SCREENING_ENABLED:
        dp.include_router(screening.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await run_health_server(bot)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
