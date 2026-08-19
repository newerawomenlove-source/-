import logging

from aiogram import Bot, F, Router
from aiogram.types import CallbackQuery, LabeledPrice, Message, PreCheckoutQuery

from bot import db
from bot.config import FREE_SPOTS_LIMIT, PAID_PRICE_RUB, PAYMENT_PROVIDER_TOKEN
from bot.keyboards import rules_keyboard
from bot.notify import notify_admin
from bot.texts import FINAL_MESSAGE, RULES_TEXT

router = Router()
logger = logging.getLogger(__name__)

INVOICE_PAYLOAD = "community_entry"


@router.callback_query(F.data == "show_rules")
async def show_rules(callback: CallbackQuery) -> None:
    user = callback.from_user
    await db.log_event(user.id, "join_clicked")
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(RULES_TEXT, reply_markup=rules_keyboard())
    await callback.answer()


@router.callback_query(F.data == "accept_rules")
async def accept_rules(callback: CallbackQuery, bot: Bot) -> None:
    user = callback.from_user
    await db.log_event(user.id, "rules_accepted")
    await callback.message.edit_reply_markup(reply_markup=None)

    occupied_spots = await db.count_occupied_spots()
    if occupied_spots < FREE_SPOTS_LIMIT:
        await db.update_user_status(user.id, "joined")
        await db.log_event(user.id, "free_joined")
        await notify_admin(bot, f"🎉 Новая резидентка приняла правила (бесплатно): @{user.username or user.id}")
        await callback.message.answer(FINAL_MESSAGE)
    elif PAYMENT_PROVIDER_TOKEN is None:
        logger.warning("Free spots exhausted but PAYMENT_PROVIDER_TOKEN is not set, letting user join for free")
        await db.update_user_status(user.id, "joined")
        await db.log_event(user.id, "join_without_payment")
        await notify_admin(bot, f"⚠️ Бесплатные места закончились, но оплата не подключена — @{user.username or user.id} вступила бесплатно")
        await callback.message.answer(FINAL_MESSAGE)
    else:
        await db.log_event(user.id, "invoice_sent")
        await bot.send_invoice(
            chat_id=callback.message.chat.id,
            title="Вступление в сообщество «Женщины нового времени»",
            description="Разовый платёж за вступление в закрытое сообщество. Без ежемесячной подписки.",
            payload=INVOICE_PAYLOAD,
            provider_token=PAYMENT_PROVIDER_TOKEN,
            currency="RUB",
            prices=[LabeledPrice(label="Вступление в сообщество", amount=PAID_PRICE_RUB * 100)],
        )

    await callback.answer()


@router.pre_checkout_query()
async def process_pre_checkout(pre_checkout_query: PreCheckoutQuery, bot: Bot) -> None:
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


@router.message(F.successful_payment)
async def process_successful_payment(message: Message, bot: Bot) -> None:
    user = message.from_user
    payment = message.successful_payment
    await db.update_user_status(user.id, "paid")
    await db.log_event(
        user.id,
        "paid_joined",
        {"amount": payment.total_amount, "currency": payment.currency},
    )
    await notify_admin(bot, f"💳 Новая резидентка оплатила вступление: @{user.username or user.id}")
    await message.answer(FINAL_MESSAGE)
