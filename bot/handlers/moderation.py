from aiogram import Bot, F, Router
from aiogram.types import CallbackQuery, InlineKeyboardButton, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot import db
from bot.config import MODERATED_TOPICS, MODERATION_CHAT_ID

router = Router()

# Модерация активна только если обе настройки заполнены — пока сообщества
# нет, эти хендлеры просто не регистрируются (см. bot/main.py).
MODERATION_ENABLED = bool(MODERATION_CHAT_ID and MODERATED_TOPICS)


def _moderation_keyboard(item_id: int):
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ Опубликовать", callback_data=f"mod_approve:{item_id}"),
        InlineKeyboardButton(text="❌ Отклонить", callback_data=f"mod_reject:{item_id}"),
    )
    return builder.as_markup()


def _is_moderated_topic(message: Message) -> bool:
    return (message.chat.id, message.message_thread_id) in MODERATED_TOPICS


@router.message(_is_moderated_topic, ~F.from_user.is_bot)
async def catch_topic_message(message: Message, bot: Bot) -> None:
    user = message.from_user
    content_type = "photo" if message.photo else "text"
    text = message.caption if message.photo else message.text
    photo_file_id = message.photo[-1].file_id if message.photo else None

    item_id = await db.create_moderation_item(
        user.id, user.username, user.first_name, message.chat.id, message.message_thread_id, content_type, text, photo_file_id
    )
    await db.log_event(user.id, "moderation_submitted", {"item_id": item_id})

    try:
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    except Exception:
        pass

    await bot.send_message(user.id, "Твоё сообщение отправлено на проверку модератору, скоро опубликуем! 🤍")

    author = f"@{user.username}" if user.username else (user.first_name or "аноним")
    chat_title = message.chat.title or str(message.chat.id)
    caption = f"Заявка от {author} — «{chat_title}», тема {message.message_thread_id}:\n\n{text or ''}"
    if photo_file_id:
        await bot.send_photo(MODERATION_CHAT_ID, photo_file_id, caption=caption, reply_markup=_moderation_keyboard(item_id))
    else:
        await bot.send_message(MODERATION_CHAT_ID, caption, reply_markup=_moderation_keyboard(item_id))


@router.callback_query(F.data.startswith("mod_approve:"))
async def approve_item(callback: CallbackQuery, bot: Bot) -> None:
    if callback.message.chat.id != int(MODERATION_CHAT_ID or 0):
        await callback.answer()
        return

    item_id = int(callback.data.split(":", 1)[1])
    item = await db.get_moderation_item(item_id)
    if not item or item["status"] != "pending":
        await callback.answer("Заявка уже обработана", show_alert=True)
        return

    author = f"@{item['username']}" if item["username"] else (item["first_name"] or "аноним")
    published_text = f"{item['text'] or ''}\n\n— {author}"

    if item["photo_file_id"]:
        await bot.send_photo(
            item["chat_id"], item["photo_file_id"], caption=published_text, message_thread_id=item["message_thread_id"]
        )
    else:
        await bot.send_message(item["chat_id"], published_text, message_thread_id=item["message_thread_id"])

    await db.resolve_moderation_item(item_id, "approved")
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.answer("Опубликовано ✅")


@router.callback_query(F.data.startswith("mod_reject:"))
async def reject_item(callback: CallbackQuery, bot: Bot) -> None:
    if callback.message.chat.id != int(MODERATION_CHAT_ID or 0):
        await callback.answer()
        return

    item_id = int(callback.data.split(":", 1)[1])
    item = await db.get_moderation_item(item_id)
    if not item or item["status"] != "pending":
        await callback.answer("Заявка уже обработана", show_alert=True)
        return

    await db.resolve_moderation_item(item_id, "rejected")
    await bot.send_message(item["tg_user_id"], "Твоё сообщение не прошло модерацию и не будет опубликовано.")
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.answer("Отклонено ❌")
