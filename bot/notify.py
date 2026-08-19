from aiogram import Bot

from bot.config import ADMIN_CHAT_ID


async def notify_admin(bot: Bot, text: str) -> None:
    if not ADMIN_CHAT_ID:
        return
    await bot.send_message(ADMIN_CHAT_ID, text)
