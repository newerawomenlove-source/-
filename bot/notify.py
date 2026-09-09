from aiogram import Bot

from bot.config import ADMIN_CHAT_IDS


async def notify_admin(bot: Bot, text: str) -> None:
    for chat_id in ADMIN_CHAT_IDS:
        await bot.send_message(chat_id, text)
