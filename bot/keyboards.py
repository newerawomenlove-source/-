from aiogram.types import InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.texts import OFFER_AGREEMENT_URL, PRIVACY_POLICY_URL, SURVEY_OPTIONS


def contact_request_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📱 Поделиться контактом", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def welcome_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Продолжить 🤍", callback_data="welcome_next"))
    return builder.as_markup()


def survey_keyboard(selected: list[str]) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    for code, short_label, _ in SURVEY_OPTIONS:
        prefix = "✅ " if code in selected else ""
        builder.row(
            InlineKeyboardButton(
                text=f"{prefix}{short_label}",
                callback_data=f"survey_toggle:{code}",
            )
        )
    builder.row(InlineKeyboardButton(text="Готово ➡️", callback_data="survey_done"))
    return builder.as_markup()


def post2_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="Вступить в сообщество", callback_data="show_rules")
    )
    return builder.as_markup()


def rules_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="ВСТУПИТЬ В СООБЩЕСТВО", callback_data="accept_rules")
    )
    builder.row(
        InlineKeyboardButton(text="Политика конфиденциальности", url=PRIVACY_POLICY_URL)
    )
    builder.row(InlineKeyboardButton(text="Договор оферты", url=OFFER_AGREEMENT_URL))
    return builder.as_markup()
