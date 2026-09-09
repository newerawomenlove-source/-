import logging

from aiogram import F, Router
from aiogram.enums import ChatType
from aiogram.types import Message

# Временный хендлер для определения chat_id/message_thread_id при настройке
# модерации. Ничего не делает с сообщением, только логирует — можно удалить
# после того, как все нужные ID собраны.

router = Router()


@router.message(F.chat.type.in_({ChatType.GROUP, ChatType.SUPERGROUP}))
async def log_group_message(message: Message) -> None:
    logging.getLogger("debug_ids").info(
        "chat_id=%s chat_title=%r message_thread_id=%s from=%s text=%r",
        message.chat.id,
        message.chat.title,
        message.message_thread_id,
        message.from_user.username if message.from_user else None,
        (message.text or message.caption or "")[:50],
    )
